from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pypdfium2 as pdfium
import pytesseract


class CliError(RuntimeError):
    pass


def parse_page_range(spec: str) -> list[int]:
    cleaned_spec = spec.replace(" ", "")
    if not cleaned_spec:
        raise CliError("--page-range must not be empty")

    pages: list[int] = []
    seen_pages: set[int] = set()

    for token in cleaned_spec.split(","):
        if not token:
            raise CliError(f"invalid page range segment in {spec!r}")

        if "-" in token:
            bounds = token.split("-")
            if len(bounds) != 2 or not bounds[0] or not bounds[1]:
                raise CliError(f"invalid page range segment {token!r}")

            start = _parse_positive_int(bounds[0], token)
            end = _parse_positive_int(bounds[1], token)
            if end < start:
                raise CliError(f"page range {token!r} must be ascending")

            candidates = range(start, end + 1)
        else:
            candidates = [_parse_positive_int(token, token)]

        for page_number in candidates:
            if page_number not in seen_pages:
                pages.append(page_number)
                seen_pages.add(page_number)

    return pages


def run_stage1_visual_extract(
    pdf_input: Path,
    page_range_spec: str,
    output_root: Path,
    run_label: str,
    scan_layout: str,
    dpi: int,
    tesseract_cmd: str | None,
) -> dict[str, object]:
    if not pdf_input.is_file():
        raise CliError(f"PDF input does not exist: {pdf_input}")
    if not run_label.strip():
        raise CliError("--run-label must not be empty")
    if not scan_layout.strip():
        raise CliError("--scan-layout must not be empty")

    selected_pages = parse_page_range(page_range_spec)
    discovery = discover_tesseract(tesseract_cmd)
    pytesseract.pytesseract.tesseract_cmd = discovery["selected_path"]

    run_root = output_root / run_label
    prep_dir = run_root / "prep" / "pdf-to-png"
    stage1_dir = run_root / "stage-1-visual-extraction"
    prep_dir.mkdir(parents=True, exist_ok=False)
    stage1_dir.mkdir(parents=True, exist_ok=False)

    document = pdfium.PdfDocument(str(pdf_input))
    page_count = len(document)
    for page_number in selected_pages:
        if page_number < 1 or page_number > page_count:
            raise CliError(
                f"selected page {page_number} is outside the PDF page count of {page_count}"
            )

    width = max(4, len(str(page_count)))
    prep_entries: list[dict[str, object]] = []
    stage1_entries: list[dict[str, object]] = []

    for page_number in selected_pages:
        page = document[page_number - 1]
        bitmap = page.render(scale=dpi / 72.0)
        image = bitmap.to_pil()

        png_name = f"pdf-page-{page_number:0{width}d}.png"
        png_path = prep_dir / png_name
        image.save(png_path, format="PNG")

        text = pytesseract.image_to_string(image)
        text_name = f"pdf-page-{page_number:0{width}d}.txt"
        text_path = stage1_dir / text_name
        text_path.write_text(text, encoding="utf-8")

        prep_entries.append(
            {
                "pdf_page": page_number,
                "png_path": _relative_path(png_path, run_root),
                "image_size_px": {"width": image.width, "height": image.height},
            }
        )

        stage1_entries.append(
            {
                "pdf_page": page_number,
                "source_png_path": _relative_path(png_path, run_root),
                "ocr_text_path": _relative_path(text_path, run_root),
                "image_size_px": {"width": image.width, "height": image.height},
                "ocr_text_length": len(text),
            }
        )

    prep_manifest = {
        "command": "stage1-visual-extract",
        "scope": "prep-only retained evidence for stage-1 proof runs",
        "pdf_input": str(pdf_input),
        "page_range": page_range_spec,
        "selected_pages": selected_pages,
        "scan_layout": scan_layout,
        "dpi": dpi,
        "generated_at_utc": _utc_now(),
        "rendered_pages": prep_entries,
    }
    _write_json(prep_dir / "manifest.json", prep_manifest)

    stage1_manifest = {
        "command": "stage1-visual-extract",
        "scope": "stage-1 visual extraction only",
        "status_note": "Later stages and final markdown artifacts are not implemented in this seam.",
        "non_normalization_note": "OCR text is retained as raw stage-1 evidence without structural reconstruction or semantic normalization.",
        "pdf_input": str(pdf_input),
        "page_range": page_range_spec,
        "selected_pages": selected_pages,
        "scan_layout": scan_layout,
        "dpi": dpi,
        "generated_at_utc": _utc_now(),
        "tesseract": discovery,
        "pages": stage1_entries,
    }
    _write_json(stage1_dir / "manifest.json", stage1_manifest)

    return {
        "run_root": str(run_root),
        "prep_manifest": str(prep_dir / "manifest.json"),
        "stage1_manifest": str(stage1_dir / "manifest.json"),
        "selected_pages": selected_pages,
        "tesseract_path": discovery["selected_path"],
    }


def discover_tesseract(explicit_cmd: str | None) -> dict[str, object]:
    if explicit_cmd:
        probe = _probe_tesseract_candidate(explicit_cmd, "explicit")
        if not probe["available"]:
            raise CliError(f"explicit Tesseract command failed: {probe['error']}")
        probes = [probe]
    else:
        probes = []
        seen_candidates: set[str] = set()

        path_candidate = shutil.which("tesseract")
        if path_candidate:
            candidate_key = _normalize_candidate_key(path_candidate)
            seen_candidates.add(candidate_key)
            probes.append(_probe_tesseract_candidate(path_candidate, "path"))

        for known_path in _known_tesseract_paths():
            candidate_key = _normalize_candidate_key(str(known_path))
            if candidate_key in seen_candidates:
                continue
            seen_candidates.add(candidate_key)
            probes.append(_probe_tesseract_candidate(str(known_path), "known-install"))

    selected_probe = next((probe for probe in probes if probe["available"]), None)
    if selected_probe is None:
        candidate_summary = "; ".join(
            f"{probe['requested']} -> {probe['error']}" for probe in probes
        ) or "no Tesseract candidates were available"
        raise CliError(f"could not resolve a working Tesseract executable: {candidate_summary}")

    return {
        "selection_rule": (
            "explicit override first, then PATH, then fixed known-install order; "
            "select the first candidate that responds to --version"
        ),
        "requested_override": explicit_cmd,
        "selected_path": selected_probe["resolved_path"],
        "selected_source": selected_probe["source"],
        "selected_version": selected_probe["version"],
        "probes": probes,
    }


def _parse_positive_int(raw_value: str, token: str) -> int:
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise CliError(f"invalid page number in segment {token!r}") from exc
    if value <= 0:
        raise CliError(f"page numbers must be positive in segment {token!r}")
    return value


def _probe_tesseract_candidate(candidate: str, source: str) -> dict[str, object]:
    resolved = _resolve_executable(candidate)
    if resolved is None:
        return {
            "source": source,
            "requested": candidate,
            "resolved_path": None,
            "available": False,
            "version": None,
            "error": "not found",
        }

    try:
        completed = subprocess.run(
            [resolved, "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return {
            "source": source,
            "requested": candidate,
            "resolved_path": resolved,
            "available": False,
            "version": None,
            "error": str(exc),
        }

    output = (completed.stdout or completed.stderr).strip()
    version_line = output.splitlines()[0].strip() if output else None
    return {
        "source": source,
        "requested": candidate,
        "resolved_path": resolved,
        "available": completed.returncode == 0,
        "version": version_line,
        "error": None if completed.returncode == 0 else output or f"exit code {completed.returncode}",
    }


def _resolve_executable(candidate: str) -> str | None:
    candidate_path = Path(candidate).expanduser()
    if candidate_path.is_file():
        return str(candidate_path.resolve())

    resolved = shutil.which(candidate)
    if resolved:
        return str(Path(resolved).resolve())

    return None


def _write_json(destination: Path, payload: dict[str, object]) -> None:
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _known_tesseract_paths() -> tuple[Path, ...]:
    paths: list[Path] = [Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")]

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        paths.append(Path(local_app_data) / "Programs" / "Tesseract-OCR" / "tesseract.exe")

    home_local = Path.home() / "AppData" / "Local" / "Programs" / "Tesseract-OCR" / "tesseract.exe"
    if home_local not in paths:
        paths.append(home_local)

    return tuple(paths)


def _relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _normalize_candidate_key(candidate: str) -> str:
    return str(Path(candidate).expanduser()).lower()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()