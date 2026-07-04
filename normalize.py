#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Edit:
    kind: str
    line_number: int | None
    before: str
    after: str
    reason: str


@dataclass
class Heading:
    level: int
    text: str
    source_line: int


@dataclass
class ReviewFlag:
    kind: str
    line_number: int | None
    text: str
    reason: str


@dataclass
class DuplicateCandidate:
    first_paragraph_index: int
    second_paragraph_index: int
    similarity: float
    first_preview: str
    second_preview: str
    recommendation: str


TOKEN_REPAIRS: dict[str, str] = {
    # Conservative browser/PDF extraction spacing repairs.
    "ofthe": "of the",
    "ofwhite": "of white",
    "ofwhiteness": "of whiteness",
    "orwhether": "or whether",
    "byvirtue": "by virtue",
    "frommy": "from my",
    "Mytheory": "My theory",
    "Myrepresentation": "My representation",
    "Frommyrepresentation": "From my representation",
    "halfof": "half of",
    "partof": "part of",
    "activity ofthe": "activity of the",
    "virtue ofthe": "virtue of the",
    "law ofcausality": "law of causality",
    "rays oflight": "rays of light",
    "one halfis": "one half is",
    "sucha": "such a",
    "white,is": "white, is",
    "whichwere": "which were",
    "geometric figures,which": "geometric figures, which",
    "experience,which": "experience, which",
    "however,the": "however, the",
    "moreweighty": "more weighty",
    "fromTheodorus": "from Theodorus",
    "don'tlet": "don't let",
    "Youmust": "You must",
    "Butthat": "But that",
    "Ithink": "I think",
    "Andwhat": "And what",
    "Sot it": "So it",
    "Well,is": "Well, is",
    "tellyou": "tell you",
    "theother": "the other",
    "injust": "in just",
    "butwhite": "but white",
    "oughtwe": "ought we",
    "doesthat": "does that",
}

KNOWN_MAJOR_HEADINGS = {
    "Contents",
    "On Vision and Colors",
    "Preface to the second edition.",
    "Introduction.",
    "First Chapter. Of vision.",
    "Chapter Two. Of the colors.",
    "Letters on The Theory of Color between Goethe and Schopenhauer",
    "A Pathography",
    "Afterword",
    "Timeline of Schopenhauer's Life",
}

SPEAKER_RE = re.compile(r"^[A-Z][A-Z'’.-]{1,25}:\s*")
SECTION_RE = re.compile(r"^\s*§\s*(\d+)\.?\s*(.*\S)?\s*$")
CHAPTER_RE = re.compile(r"^\s*(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\s+Chapter\.\s+.+", re.I)
TIMELINE_ENTRY_RE = re.compile(r"^\s*(1[789]\d{2}|20\d{2})\s*[-–]\s+.+")
PAGE_NUMBER_RE = re.compile(r"^\s*(?:[ivxlcdm]+|[i1][o0]|\d{1,4})\s*$", re.I)
STANDALONE_STEPHANUS_RE = re.compile(r"^\s*(?:\d{3,4}[a-eA-Eа-сА-С]?|[a-eA-Eа-сА-С])\s*$")
INLINE_STEPHANUS_RE = re.compile(r"\b\d{3,4}\s*[a-eA-Eа-сА-С]\b")
TRAILING_SINGLE_REF_RE = re.compile(r"([*!?;:])\s+[b-eB-EсС]\s*$")
LEADING_SINGLE_REF_BEFORE_SPEAKER_RE = re.compile(r"^\s*[a-eA-Eа-сА-С]\s+(?=[A-Z][A-Z'’.-]{1,25}:)")
ALL_CAPS_HEADING_RE = re.compile(r"^[A-Z0-9][A-Z0-9 '\-–—?:;,.&]+$")
SUSPICIOUS_RE = re.compile(
    r"(\b\w{1,2}[-–]\w{1,2}\b|[A-Za-z]+N\b|\bff\w+|\bNense\b|\bRoth\b|\bsoome\b|\bt0\b|\bto0\b|\basso\b)"
)


def count_by_kind(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_heading_text(text: str) -> str:
    text = collapse_spaces(text)
    text = re.sub(r"\s+(\d{3,4}[a-eA-E])$", "", text)  # heading trailing refs like 143C
    text = text.replace("Production ofwhite", "Production of white")
    text = text.replace("activity ofthe", "activity of the")
    return text.strip()


def is_page_number_line(line: str) -> bool:
    return bool(PAGE_NUMBER_RE.match(line.strip()))


def is_reference_marker_line(line: str, reference_style: str) -> bool:
    if reference_style == "stephanus":
        return bool(STANDALONE_STEPHANUS_RE.match(line.strip()))
    return False


def is_running_header(line: str, title: str) -> bool:
    stripped = collapse_spaces(line).strip("*")
    title_norm = collapse_spaces(title).upper()
    if stripped.upper() == title_norm:
        return True
    return False


def classify_heading(line: str, title: str) -> tuple[int, str] | None:
    stripped = normalize_heading_text(line)
    if not stripped:
        return None

    # Main title.
    if stripped.upper() == title.upper():
        return (1, title)

    section_match = SECTION_RE.match(stripped)
    if section_match:
        number = section_match.group(1)
        rest = normalize_heading_text(section_match.group(2) or "")
        return (3, f"§ {number}" + (f". {rest}" if rest else ""))

    if CHAPTER_RE.match(stripped):
        return (2, stripped.rstrip("."))

    if stripped in KNOWN_MAJOR_HEADINGS:
        if stripped == "Contents":
            return (2, "Contents")
        return (2, stripped.rstrip("."))

    if TIMELINE_ENTRY_RE.match(stripped):
        return (3, stripped)

    # Dialogue/book section headings: WHAT IS KNOWLEDGE?, DICE AND SIZE PUZZLES, etc.
    # Avoid speaker names and running headers by excluding very short all-caps single-word lines.
    if ALL_CAPS_HEADING_RE.match(stripped):
        words = stripped.split()
        if len(words) >= 2 and not stripped.endswith(":"):
            return (2, stripped)

    return None


def clean_reference_noise(line: str, line_no: int, reference_style: str, edits: list[Edit]) -> str:
    cleaned = line
    if reference_style != "stephanus":
        return cleaned

    old = cleaned
    cleaned = INLINE_STEPHANUS_RE.sub("", cleaned)
    if cleaned != old:
        edits.append(Edit(
            kind="reference_marker_removed",
            line_number=line_no,
            before=old,
            after=cleaned,
            reason="Removed inline Stephanus-style reference marker such as 142a / 143C.",
        ))

    old = cleaned
    cleaned = LEADING_SINGLE_REF_BEFORE_SPEAKER_RE.sub("", cleaned)
    if cleaned != old:
        edits.append(Edit(
            kind="reference_marker_removed",
            line_number=line_no,
            before=old,
            after=cleaned,
            reason="Removed leading single-letter margin marker before speaker label.",
        ))

    old = cleaned
    # Very conservative trailing marker cleanup. Only b-e after *, !, ?, ;, or : is stripped.
    # Do NOT strip trailing "a", because browser PDF wraps often leave a real article at line end.
    cleaned2 = TRAILING_SINGLE_REF_RE.sub(r"\1", cleaned)
    if cleaned2 != cleaned:
        cleaned = cleaned2
        edits.append(Edit(
            kind="reference_marker_removed",
            line_number=line_no,
            before=old,
            after=cleaned,
            reason="Removed low-risk trailing single-letter Stephanus margin marker.",
        ))

    return cleaned


def apply_token_repairs(text: str, source_line: int | None, edits: list[Edit]) -> str:
    repaired = text
    for before, after in TOKEN_REPAIRS.items():
        if before in repaired:
            old = repaired
            repaired = repaired.replace(before, after)
            edits.append(Edit(
                kind="token_spacing_repair",
                line_number=source_line,
                before=old,
                after=repaired,
                reason=f"Explicit conservative repair: {before!r} -> {after!r}.",
            ))

    old = repaired
    repaired = re.sub(r"([,;:])(?=[A-Za-z])", r"\1 ", repaired)
    repaired = re.sub(r"([a-z])\.([A-Z])", r"\1. \2", repaired)
    repaired = re.sub(r"\s+", " ", repaired).strip()
    if repaired != old:
        edits.append(Edit(
            kind="punctuation_spacing_repair",
            line_number=source_line,
            before=old,
            after=repaired,
            reason="Inserted obvious missing spaces after punctuation and collapsed repeated whitespace.",
        ))
    return repaired


def should_start_new_paragraph(previous: str, current: str, title: str) -> bool:
    prev = previous.strip()
    cur = current.strip()
    if not prev or not cur:
        return True
    if classify_heading(cur, title) or classify_heading(prev, title):
        return True
    if SPEAKER_RE.match(cur):
        return True
    if cur.startswith(("- ", "– ", "— ")) and len(cur) < 120:
        return True
    if TIMELINE_ENTRY_RE.match(cur):
        return True
    if re.search(r"[.!?][\"')\]]?$", prev) and cur[:1].isupper():
        return True
    return False


def should_join(previous: str, current: str, title: str) -> bool:
    if should_start_new_paragraph(previous, current, title):
        return False
    prev = previous.rstrip()
    cur = current.lstrip()
    if prev.endswith("-") and cur[:1].islower():
        return True
    if prev.endswith((",", ";", ":", "—", "–")):
        return True
    if cur[:1].islower():
        return True
    if len(prev) >= 35 and not re.search(r"[.!?;:]$", prev):
        return True
    return False


def split_embedded_speakers(text: str) -> list[str]:
    """Split accidental joined dialogue turns: '... text. SOCRATES: ...'"""
    # No capture group here; captured speakers caused duplicated labels in v2 draft.
    parts = re.split(r"\s+(?=[A-Z][A-Z'’.-]{1,25}:\s)", text)
    return [p.strip() for p in parts if p.strip()]


def preprocess_lines(raw_lines: list[str], title: str, reference_style: str, edits: list[Edit]) -> list[tuple[int, str]]:
    kept: list[tuple[int, str]] = []
    title_seen = False

    for line_no, raw in enumerate(raw_lines, start=1):
        line = raw.strip()
        if not line:
            kept.append((line_no, ""))
            continue

        if is_page_number_line(line):
            edits.append(Edit("page_number_removed", line_no, raw, "", "Removed standalone page-number line."))
            kept.append((line_no, ""))
            continue

        if is_reference_marker_line(line, reference_style):
            edits.append(Edit("reference_marker_line_removed", line_no, raw, "", "Removed standalone margin/reference marker line."))
            kept.append((line_no, ""))
            continue

        if is_running_header(line, title):
            if not title_seen:
                title_seen = True
                kept.append((line_no, line))
            else:
                edits.append(Edit("running_header_removed", line_no, raw, "", "Removed repeated running header matching title."))
                kept.append((line_no, ""))
            continue

        cleaned = clean_reference_noise(line, line_no, reference_style, edits)
        kept.append((line_no, cleaned.strip()))

    return kept


def build_blocks(lines: list[tuple[int, str]], title: str, edits: list[Edit]) -> list[tuple[int | None, str]]:
    blocks: list[tuple[int | None, str]] = []
    current = ""
    current_line: int | None = None

    def flush() -> None:
        nonlocal current, current_line
        if current.strip():
            for part in split_embedded_speakers(current.strip()):
                blocks.append((current_line, part))
        current = ""
        current_line = None

    for line_no, line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue

        if classify_heading(stripped, title):
            flush()
            blocks.append((line_no, normalize_heading_text(stripped)))
            continue

        if not current:
            current = stripped
            current_line = line_no
            continue

        if should_join(current, stripped, title):
            old = current
            if current.endswith("-") and stripped[:1].islower():
                current = current[:-1] + stripped
            else:
                current = f"{current} {stripped}"
            edits.append(Edit("line_wrap_join", line_no, old + "\n" + stripped, current, "Joined probable PDF hard-wrap."))
        else:
            flush()
            current = stripped
            current_line = line_no

    flush()
    return blocks


def blocks_to_markdown(blocks: list[tuple[int | None, str]], title: str, edits: list[Edit], flags: list[ReviewFlag]) -> tuple[str, list[Heading]]:
    out: list[str] = []
    headings: list[Heading] = []
    title_written = False

    def ensure_title() -> None:
        nonlocal title_written
        if not title_written:
            out.append(f"# {title}")
            out.append("")
            headings.append(Heading(1, title, 0))
            title_written = True

    for line_no, block in blocks:
        block = apply_token_repairs(block, line_no, edits)
        heading = classify_heading(block, title)

        if heading:
            level, heading_text = heading
            if level == 1 and heading_text.upper() == title.upper():
                ensure_title()
                continue
            ensure_title()
            if level == 1:
                level = 2
            out.append(f"{'#' * level} {heading_text}")
            out.append("")
            headings.append(Heading(level, heading_text, line_no or -1))
            continue

        ensure_title()

        if SUSPICIOUS_RE.search(block):
            flags.append(ReviewFlag(
                "suspicious_extraction_artifact",
                line_no,
                block[:260],
                "Token pattern may indicate PDF/browser extraction corruption.",
            ))

        if block.startswith(("- ", "– ", "— ")) and len(block) < 120:
            out.append(f"> {block}")
        else:
            out.append(block)
        out.append("")

    return "\n".join(out).strip() + "\n", headings


def markdown_paragraphs(markdown: str) -> list[str]:
    paras: list[str] = []
    cur: list[str] = []
    for line in markdown.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            if cur:
                paras.append(" ".join(cur).strip())
                cur = []
            continue
        if s.startswith(">"):
            if cur:
                paras.append(" ".join(cur).strip())
                cur = []
            paras.append(s.lstrip("> ").strip())
            continue
        cur.append(s)
    if cur:
        paras.append(" ".join(cur).strip())
    return [p for p in paras if len(p) >= 80]


def corruption_score(text: str) -> int:
    score = 0
    score += len(re.findall(r"\b\w{1,2}[-–]\w{1,2}\b", text)) * 3
    score += len(re.findall(r"[A-Za-z]+N\b", text)) * 4
    score += len(re.findall(r"\bff\w+", text)) * 2
    score += len(re.findall(r"\b(?:Nense|Roth|lirmament|ffleulty|whitenesN)\b", text)) * 4
    return score


def detect_duplicates(paragraphs: list[str]) -> list[DuplicateCandidate]:
    norm = [re.sub(r"[^a-z0-9]+", " ", p.lower()).strip() for p in paragraphs]
    candidates: list[DuplicateCandidate] = []
    for i in range(len(norm)):
        if len(norm[i]) < 250:
            continue
        for j in range(i + 1, min(i + 25, len(norm))):
            if len(norm[j]) < 250:
                continue
            ratio = difflib.SequenceMatcher(None, norm[i], norm[j]).ratio()
            if ratio >= 0.72:
                s1, s2 = corruption_score(paragraphs[i]), corruption_score(paragraphs[j])
                if s1 > s2:
                    rec = "manual_review_prefer_second"
                elif s2 > s1:
                    rec = "manual_review_prefer_first"
                else:
                    rec = "manual_review_no_clear_preference"
                candidates.append(DuplicateCandidate(i, j, round(ratio, 3), paragraphs[i][:300], paragraphs[j][:300], rec))
    return candidates


def write_review_flags(path: Path, flags: list[ReviewFlag]) -> None:
    lines = ["# Manual Review Flags", ""]
    if not flags:
        lines.append("No manual review flags generated.")
    for idx, flag in enumerate(flags, start=1):
        lines += [f"## {idx}. {flag.kind}", "", f"- Source line: {flag.line_number}", f"- Reason: {flag.reason}", "", "```text", flag.text, "```", ""]
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def normalize(input_path: Path, out_dir: Path, title: str, reference_style: str) -> None:
    raw_lines = input_path.read_text(encoding="utf-8-sig").splitlines()
    out_dir.mkdir(parents=True, exist_ok=True)

    edits: list[Edit] = []
    flags: list[ReviewFlag] = []

    preprocessed = preprocess_lines(raw_lines, title, reference_style, edits)
    blocks = build_blocks(preprocessed, title, edits)
    markdown, headings = blocks_to_markdown(blocks, title, edits, flags)
    paragraphs = markdown_paragraphs(markdown)
    duplicates = detect_duplicates(paragraphs)

    for dup in duplicates:
        flags.append(ReviewFlag(
            "duplicate_candidate",
            None,
            f"Paragraph {dup.first_paragraph_index} vs {dup.second_paragraph_index}; similarity={dup.similarity}; {dup.recommendation}",
            "Fuzzy near-duplicate text detected. Not automatically removed.",
        ))

    (out_dir / "normalized.md").write_text(markdown, encoding="utf-8")
    (out_dir / "duplicate_candidates.json").write_text(json.dumps([asdict(d) for d in duplicates], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_review_flags(out_dir / "manual_review_flags.md", flags)

    report = {
        "input_file": str(input_path),
        "title": title,
        "reference_style": reference_style,
        "raw_line_count": len(raw_lines),
        "output_file": str(out_dir / "normalized.md"),
        "heading_count": len(headings),
        "headings": [asdict(h) for h in headings],
        "paragraph_count_estimate": len(paragraphs),
        "edit_count": len(edits),
        "edit_counts_by_kind": count_by_kind(e.kind for e in edits),
        "review_flag_count": len(flags),
        "review_flag_counts_by_kind": count_by_kind(f.kind for f in flags),
        "duplicate_candidate_count": len(duplicates),
        "notes": [
            "Raw input was not modified.",
            "This version does not drop the table of contents by default; the prior aggressive TOC-skipping bug was removed.",
            "Standalone page numbers are removed.",
            "Stephanus/reference markers are removed only when --reference-style stephanus is used.",
            "Duplicate candidates are reported only; no duplicate text is automatically deleted.",
            "Suspicious extraction artifacts are flagged for review.",
        ],
    }
    (out_dir / "normalization_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "normalized": str(out_dir / "normalized.md"),
        "report": str(out_dir / "normalization_report.json"),
        "review_flags": str(out_dir / "manual_review_flags.md"),
        "duplicate_candidates": str(out_dir / "duplicate_candidates.json"),
        "raw_line_count": len(raw_lines),
        "heading_count": len(headings),
        "paragraph_count_estimate": len(paragraphs),
        "edit_count": len(edits),
        "review_flag_count": len(flags),
        "duplicate_candidate_count": len(duplicates),
    }, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize browser-copied PDF text into Markdown.")
    parser.add_argument("input", type=Path, help="Raw browser-copy text file")
    parser.add_argument("--out-dir", type=Path, default=Path("normalized_output"), help="Output directory")
    parser.add_argument("--title", default="Untitled", help="Top-level Markdown title")
    parser.add_argument(
        "--reference-style",
        choices=["none", "stephanus"],
        default="none",
        help="Optional margin/reference marker cleanup. Use 'stephanus' for Plato-style 142a/b/c/d markers.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.input.is_file():
        raise SystemExit(f"Input file does not exist: {args.input}")
    normalize(args.input, args.out_dir, args.title, args.reference_style)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
