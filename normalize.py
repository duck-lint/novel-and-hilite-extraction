#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


# ----------------------------
# Data models
# ----------------------------

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
class DuplicateCandidate:
    first_paragraph_index: int
    second_paragraph_index: int
    similarity: float
    first_preview: str
    second_preview: str
    recommendation: str


@dataclass
class ReviewFlag:
    kind: str
    line_number: int | None
    text: str
    reason: str


# ----------------------------
# Tunable rules
# ----------------------------

# Very conservative spacing repairs. Keep this list explicit.
# Add to it only when you see recurring extraction artifacts in raw browser-copy text.
TOKEN_REPAIRS: dict[str, str] = {
    "ofthe": "of the",
    "ofThe": "of The",
    "ofwhite": "of white",
    "ofwhiteness": "of whiteness",
    "orwhether": "or whether",
    "byvirtue": "by virtue",
    "frommy": "from my",
    "Mytheory": "My theory",
    "Myrepresentation": "My representation",
    "Frommyrepresentation": "From my representation",
    "ana undivided": "an undivided",
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
    "retina's activity": "retina's activity",
}

# Known section-like titles from the uploaded book text.
# This prevents the normalizer from needing to infer every major heading from scratch.
MAJOR_HEADINGS = {
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

# If a line is this short and looks like a page number, it is removed from body output.
PAGE_NUMBER_RE = re.compile(r"^\s*(?:[ivxlcdm]+|\d{1,4})\s*$", re.IGNORECASE)

SECTION_RE = re.compile(r"^\s*§\s*(\d+)\.?\s*(.*\S)?\s*$")
CHAPTER_RE = re.compile(r"^\s*(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\s+Chapter\.\s+.+", re.IGNORECASE)
LETTER_NUMBER_RE = re.compile(r"^\s*\d{1,2}\.\s*$")
TIMELINE_ENTRY_RE = re.compile(r"^\s*(1[789]\d{2}|20\d{2})\s*[-–]\s+.+")

# Lines with obvious extraction corruption. These are not automatically fixed.
SUSPICIOUS_RE = re.compile(
    r"("
    r"[A-Za-z]{1,2}[A-Z][a-z]|"          # weird mid-token capital
    r"[A-Za-z]+N\b|"                     # whitenesN-like
    r"\b[Ii]h\b|"
    r"\bff\w+|"
    r"\b\w{1,2}[-–]\w{1,2}\b|"
    r"[\"“][a-z]-\s|"
    r"\bNense\b|"
    r"\bRoth\b"
    r")"
)


# ----------------------------
# Parsing helpers
# ----------------------------

def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig").splitlines()


def is_page_number_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if PAGE_NUMBER_RE.match(stripped) is None:
        return False
    # Keep one- or two-digit numbered letters only when surrounded later by letter content?
    # At the raw-cleaning phase, a bare number is usually a page number in browser PDF paste.
    return True


def normalize_heading_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    text = text.replace("Production ofwhite", "Production of white")
    text = text.replace("activity ofthe", "activity of the")
    return text


def classify_heading(line: str, pending_line: str | None = None) -> tuple[int, str] | None:
    """
    Return (markdown_level, heading_text) or None.

    Heading policy:
    - # is reserved for the document title.
    - ## major work/chapter/frontmatter/backmatter headings.
    - ### numbered sections like § 10.
    - #### numbered letters in correspondence sections.
    """
    stripped = normalize_heading_text(line)

    if not stripped:
        return None

    # Contents line can be useful but should not become part of the body outline.
    if stripped == "Contents":
        return (2, "Contents")

    # §10. Heading
    section_match = SECTION_RE.match(stripped)
    if section_match:
        section_number = section_match.group(1)
        title = section_match.group(2) or ""
        title = normalize_heading_text(title)
        heading_text = f"§ {section_number}"
        if title:
            heading_text += f". {title}"
        return (3, heading_text)

    if CHAPTER_RE.match(stripped):
        return (2, stripped.rstrip("."))

    if stripped in MAJOR_HEADINGS:
        # If this is the title, caller may demote or skip duplicate title separately.
        if stripped == "On Vision and Colors":
            return (1, stripped)
        return (2, stripped.rstrip("."))

    # Some TOC/body headings wrap across two lines.
    if pending_line:
        combined = normalize_heading_text(f"{stripped} {pending_line}")
        if combined in MAJOR_HEADINGS:
            return (2, combined.rstrip("."))

    # Letter sections are meaningful under "Letters..."
    if LETTER_NUMBER_RE.match(stripped):
        return (4, stripped)

    # Timeline entries are useful semantic anchors.
    if TIMELINE_ENTRY_RE.match(stripped):
        return (3, stripped)

    return None


def apply_token_repairs(text: str, source_line: int | None, edits: list[Edit]) -> str:
    repaired = text
    for before, after in TOKEN_REPAIRS.items():
        if before in repaired:
            old = repaired
            repaired = repaired.replace(before, after)
            edits.append(
                Edit(
                    kind="token_spacing_repair",
                    line_number=source_line,
                    before=old,
                    after=repaired,
                    reason=f"Applied explicit conservative repair: {before!r} -> {after!r}",
                )
            )

    # Punctuation spacing: only obvious missing space after comma/period when followed by a letter.
    old = repaired
    repaired = re.sub(r"([,;:])(?=[A-Za-z])", r"\1 ", repaired)
    repaired = re.sub(r"([a-z])\.([A-Z])", r"\1. \2", repaired)
    if repaired != old:
        edits.append(
            Edit(
                kind="punctuation_spacing_repair",
                line_number=source_line,
                before=old,
                after=repaired,
                reason="Inserted missing space after punctuation in conservative contexts.",
            )
        )

    return repaired


def should_join_lines(current: str, next_line: str) -> bool:
    """
    Decide whether two raw PDF lines are part of the same paragraph.

    Conservative bias:
    - Join normal wrapped prose.
    - Do not join headings, blank lines, page numbers, timeline entries, or standalone notes.
    """
    cur = current.rstrip()
    nxt = next_line.lstrip()

    if not cur or not nxt:
        return False
    if is_page_number_line(cur) or is_page_number_line(nxt):
        return False
    if classify_heading(cur) or classify_heading(nxt):
        return False
    if TIMELINE_ENTRY_RE.match(nxt):
        return False
    if nxt.startswith(("-", "–", "—")) and len(nxt) < 80:
        return False

    # Hyphenated line break.
    if cur.endswith("-") and nxt and nxt[0].islower():
        return True

    # Strong sentence-ending punctuation usually indicates a possible paragraph boundary,
    # but PDF line wraps can still put the next sentence immediately after.
    # We choose not to join after terminal punctuation when the next line begins uppercase.
    if re.search(r"[.!?][\"')\]]?$", cur) and nxt[:1].isupper():
        return False

    # Colon followed by continuation often belongs together.
    if cur.endswith(":"):
        return True

    # Semicolon/comma almost always continues.
    if cur.endswith((",", ";")):
        return True

    # If the next line begins lowercase, it is almost certainly a continuation.
    if nxt[:1].islower():
        return True

    # Long-ish current line without terminal punctuation likely wraps.
    if len(cur) >= 35 and not re.search(r"[.!?;:]$", cur):
        return True

    return False


def join_wrapped_lines(lines: list[tuple[int, str]], edits: list[Edit]) -> list[tuple[int | None, str]]:
    """
    Convert raw lines into preliminary blocks:
    - headings remain individual blocks
    - paragraphs are joined from wrapped lines
    - page number lines are dropped
    """
    blocks: list[tuple[int | None, str]] = []
    current_line_no: int | None = None
    current = ""

    def flush() -> None:
        nonlocal current, current_line_no
        if current.strip():
            blocks.append((current_line_no, current.strip()))
        current = ""
        current_line_no = None

    i = 0
    while i < len(lines):
        line_no, raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush()
            i += 1
            continue

        if is_page_number_line(stripped):
            edits.append(
                Edit(
                    kind="page_number_removed",
                    line_number=line_no,
                    before=raw,
                    after="",
                    reason="Removed standalone page-number line.",
                )
            )
            flush()
            i += 1
            continue

        # Preserve headings as separate blocks.
        if classify_heading(stripped):
            flush()
            blocks.append((line_no, normalize_heading_text(stripped)))
            i += 1
            continue

        if not current:
            current = stripped
            current_line_no = line_no
            i += 1
            continue

        if should_join_lines(current, stripped):
            old = current
            if current.endswith("-") and stripped[:1].islower():
                current = current[:-1] + stripped
            else:
                current = current + " " + stripped
            edits.append(
                Edit(
                    kind="line_wrap_join",
                    line_number=line_no,
                    before=old + "\n" + stripped,
                    after=current,
                    reason="Joined probable PDF hard-wrapped prose line.",
                )
            )
        else:
            flush()
            current = stripped
            current_line_no = line_no

        i += 1

    flush()
    return blocks


def markdown_blocks(
    blocks: list[tuple[int | None, str]],
    title: str,
    edits: list[Edit],
    review_flags: list[ReviewFlag],
    include_contents: bool,
) -> tuple[str, list[Heading]]:
    """
    Convert preliminary blocks into Markdown, applying heading detection and token repairs.
    """
    output: list[str] = []
    headings: list[Heading] = []
    title_written = False
    in_contents = False

    for source_line, block in blocks:
        repaired = apply_token_repairs(block, source_line, edits)
        heading = classify_heading(repaired)

        if heading:
            level, heading_text = heading

            # Drop TOC if requested. For semantic traversal, the body headings matter more.
            if heading_text == "Contents":
                in_contents = True
                if not include_contents:
                    continue

            # End contents when the actual title/body begins after TOC page marker.
            if in_contents and heading_text == title:
                in_contents = False

            if in_contents and not include_contents:
                continue

            # Avoid duplicate # title if caller provided one.
            if level == 1 and heading_text == title:
                if not title_written:
                    output.append(f"# {heading_text}")
                    output.append("")
                    title_written = True
                    headings.append(Heading(level=1, text=heading_text, source_line=source_line or -1))
                continue

            if not title_written:
                output.append(f"# {title}")
                output.append("")
                title_written = True
                headings.append(Heading(level=1, text=title, source_line=0))

            # Demote any additional level-1 headings to level 2 under the document title.
            if level == 1:
                level = 2

            output.append(f"{'#' * level} {heading_text}")
            output.append("")
            headings.append(Heading(level=level, text=heading_text, source_line=source_line or -1))
            continue

        if in_contents and not include_contents:
            continue

        if not title_written:
            output.append(f"# {title}")
            output.append("")
            title_written = True
            headings.append(Heading(level=1, text=title, source_line=0))

        if SUSPICIOUS_RE.search(repaired):
            review_flags.append(
                ReviewFlag(
                    kind="suspicious_extraction_artifact",
                    line_number=source_line,
                    text=repaired[:240],
                    reason="Contains token pattern that may indicate browser/PDF extraction corruption.",
                )
            )

        # Preserve short marginalia / operator notes as blockquotes to avoid blending into body.
        if repaired.startswith(("- ", "– ", "— ")) and len(repaired) < 120:
            output.append(f"> {repaired}")
            output.append("")
        else:
            output.append(repaired)
            output.append("")

    return "\n".join(output).strip() + "\n", headings


def paragraphs_from_markdown(markdown: str) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []

    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue
        if stripped.startswith(">"):
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            paragraphs.append(stripped.lstrip("> ").strip())
            continue
        current.append(stripped)

    if current:
        paragraphs.append(" ".join(current).strip())

    return [p for p in paragraphs if len(p) >= 80]


def corruption_score(text: str) -> int:
    """
    Higher score means more likely corrupted.
    Crude but useful for duplicate review recommendations.
    """
    score = 0
    score += len(re.findall(r"\b\w{1,2}[-–]\w{1,2}\b", text)) * 3
    score += len(re.findall(r"\b[A-Za-z]{1,2}\b", text))
    score += len(re.findall(r"[A-Za-z]+N\b", text)) * 4
    score += len(re.findall(r"\bff\w+", text)) * 2
    score += len(re.findall(r"\b(?:Ih|Nense|Roth|lirmament|ffleulty)\b", text)) * 4
    score += len(re.findall(r"\s{2,}", text))
    return score


def detect_duplicate_candidates(paragraphs: list[str]) -> list[DuplicateCandidate]:
    """
    Find likely duplicate paragraphs/sections caused by rescanned or reselected pages.
    This does not delete anything. It only reports candidates.
    """
    candidates: list[DuplicateCandidate] = []

    normalized = [
        re.sub(r"[^a-z0-9]+", " ", p.lower()).strip()
        for p in paragraphs
    ]

    for i in range(len(normalized)):
        if len(normalized[i]) < 250:
            continue
        # Limit compare window to nearby-ish paragraphs for speed and relevance.
        for j in range(i + 1, min(len(normalized), i + 25)):
            if len(normalized[j]) < 250:
                continue
            ratio = difflib.SequenceMatcher(None, normalized[i], normalized[j]).ratio()
            if ratio >= 0.72:
                first_score = corruption_score(paragraphs[i])
                second_score = corruption_score(paragraphs[j])
                if first_score > second_score:
                    recommendation = "manual_review_prefer_second"
                elif second_score > first_score:
                    recommendation = "manual_review_prefer_first"
                else:
                    recommendation = "manual_review_no_clear_preference"

                candidates.append(
                    DuplicateCandidate(
                        first_paragraph_index=i,
                        second_paragraph_index=j,
                        similarity=round(ratio, 3),
                        first_preview=paragraphs[i][:300],
                        second_preview=paragraphs[j][:300],
                        recommendation=recommendation,
                    )
                )

    return candidates


def write_review_flags(path: Path, flags: list[ReviewFlag]) -> None:
    lines = ["# Manual Review Flags", ""]
    if not flags:
        lines.append("No manual review flags generated.")
    else:
        for idx, flag in enumerate(flags, start=1):
            lines.append(f"## {idx}. {flag.kind}")
            lines.append("")
            lines.append(f"- Source line: {flag.line_number}")
            lines.append(f"- Reason: {flag.reason}")
            lines.append("")
            lines.append("```text")
            lines.append(flag.text)
            lines.append("```")
            lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def normalize_file(
    input_path: Path,
    out_dir: Path,
    title: str,
    include_contents: bool,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_lines = read_lines(input_path)
    numbered_lines = list(enumerate(raw_lines, start=1))

    edits: list[Edit] = []
    review_flags: list[ReviewFlag] = []

    blocks = join_wrapped_lines(numbered_lines, edits)
    markdown, headings = markdown_blocks(
        blocks=blocks,
        title=title,
        edits=edits,
        review_flags=review_flags,
        include_contents=include_contents,
    )

    paragraphs = paragraphs_from_markdown(markdown)
    duplicate_candidates = detect_duplicate_candidates(paragraphs)

    # Duplicate candidates are review flags, not automatic deletion.
    for candidate in duplicate_candidates:
        review_flags.append(
            ReviewFlag(
                kind="duplicate_candidate",
                line_number=None,
                text=(
                    f"Paragraph {candidate.first_paragraph_index} vs "
                    f"{candidate.second_paragraph_index}; similarity={candidate.similarity}; "
                    f"recommendation={candidate.recommendation}"
                ),
                reason="Fuzzy near-duplicate paragraph detected. Review before deleting or merging.",
            )
        )

    normalized_path = out_dir / "normalized.md"
    report_path = out_dir / "normalization_report.json"
    flags_path = out_dir / "manual_review_flags.md"
    duplicates_path = out_dir / "duplicate_candidates.json"

    normalized_path.write_text(markdown, encoding="utf-8")

    report = {
        "input_file": str(input_path),
        "title": title,
        "raw_line_count": len(raw_lines),
        "output_file": str(normalized_path),
        "output_paragraph_count_estimate": len(paragraphs),
        "heading_count": len(headings),
        "headings": [asdict(h) for h in headings],
        "edit_count": len(edits),
        "edit_counts_by_kind": count_by_kind(edit.kind for edit in edits),
        "review_flag_count": len(review_flags),
        "review_flag_counts_by_kind": count_by_kind(flag.kind for flag in review_flags),
        "duplicate_candidate_count": len(duplicate_candidates),
        "notes": [
            "Raw input was not modified.",
            "Standalone page-number lines were removed from normalized output.",
            "Line wraps were joined using conservative PDF-copy heuristics.",
            "Duplicate candidates are reported only; no duplicate text is automatically deleted.",
            "Suspicious extraction artifacts are flagged for manual review.",
            "Token repairs are explicit and conservative; extend TOKEN_REPAIRS as needed.",
        ],
    }

    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    duplicates_path.write_text(
        json.dumps([asdict(c) for c in duplicate_candidates], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_review_flags(flags_path, review_flags)

    print(json.dumps({
        "normalized": str(normalized_path),
        "report": str(report_path),
        "review_flags": str(flags_path),
        "duplicate_candidates": str(duplicates_path),
        "raw_line_count": len(raw_lines),
        "heading_count": len(headings),
        "paragraph_count_estimate": len(paragraphs),
        "edit_count": len(edits),
        "review_flag_count": len(review_flags),
        "duplicate_candidate_count": len(duplicate_candidates),
    }, indent=2))


def count_by_kind(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize raw browser-copied PDF text into semantic-ingestion-friendly Markdown."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Raw browser-copy text file.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("normalized_output"),
        help="Output directory. Default: normalized_output",
    )
    parser.add_argument(
        "--title",
        default="On Vision and Colors",
        help="Document title for the top-level Markdown heading.",
    )
    parser.add_argument(
        "--include-contents",
        action="store_true",
        help="Keep the table of contents in normalized.md. Default is to drop it.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.input.is_file():
        raise SystemExit(f"Input file does not exist: {args.input}")

    normalize_file(
        input_path=args.input,
        out_dir=args.out_dir,
        title=args.title,
        include_contents=args.include_contents,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
