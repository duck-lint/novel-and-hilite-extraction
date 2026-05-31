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
    spread_handling: str,
    dpi: int,
    outer_crop_px: int,
    gutter_crop_px: int,
    top_crop_px: int,
    bottom_crop_px: int,
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
    resolved_spread_handling = _resolve_spread_handling(scan_layout, spread_handling)

    run_root = output_root / run_label
    prep_dir = run_root / "prep" / "pdf-to-png"
    derived_dir = run_root / "prep" / "derived-surfaces"
    stage1_dir = run_root / "stage-1-visual-extraction"
    prep_dir.mkdir(parents=True, exist_ok=False)
    derived_dir.mkdir(parents=True, exist_ok=False)
    stage1_dir.mkdir(parents=True, exist_ok=False)

    preprocess_controls = {
        "scan_layout": scan_layout,
        "requested_spread_handling": spread_handling,
        "resolved_spread_handling": resolved_spread_handling,
        "dpi": dpi,
        "outer_crop_px": outer_crop_px,
        "gutter_crop_px": gutter_crop_px,
        "top_crop_px": top_crop_px,
        "bottom_crop_px": bottom_crop_px,
    }

    document = pdfium.PdfDocument(str(pdf_input))
    try:
        page_count = len(document)
        for page_number in selected_pages:
            if page_number < 1 or page_number > page_count:
                raise CliError(
                    f"selected page {page_number} is outside the PDF page count of {page_count}"
                )

        width = max(4, len(str(page_count)))
        prep_entries: list[dict[str, object]] = []
        derived_surface_entries: list[dict[str, object]] = []
        stage1_entries: list[dict[str, object]] = []

        for page_number in selected_pages:
            page = document[page_number - 1]
            try:
                bitmap = page.render(scale=dpi / 72.0)
                image = bitmap.to_pil()
            finally:
                if hasattr(page, "close"):
                    page.close()

            png_name = f"pdf-page-{page_number:0{width}d}.png"
            png_path = prep_dir / png_name
            image.save(png_path, format="PNG")

            surface_specs = _build_surface_specs(
                pdf_page=page_number,
                page_width=image.width,
                page_height=image.height,
                width_padding=width,
                spread_handling=resolved_spread_handling,
                outer_crop_px=outer_crop_px,
                gutter_crop_px=gutter_crop_px,
                top_crop_px=top_crop_px,
                bottom_crop_px=bottom_crop_px,
            )

            prep_entries.append(
                {
                    "pdf_page": page_number,
                    "png_path": _relative_path(png_path, run_root),
                    "image_size_px": {"width": image.width, "height": image.height},
                    "derived_surface_ids": [surface_spec["surface_id"] for surface_spec in surface_specs],
                }
            )

            for surface_spec in surface_specs:
                crop_box = surface_spec["crop_box_px"]
                derived_image = image.crop(
                    (
                        crop_box["left"],
                        crop_box["top"],
                        crop_box["right"],
                        crop_box["bottom"],
                    )
                )
                derived_png_path = derived_dir / f"{surface_spec['surface_id']}.png"
                derived_image.save(derived_png_path, format="PNG")

                ocr_result = _run_ocr(derived_image)
                text_path = stage1_dir / f"{surface_spec['surface_id']}.txt"
                text_path.write_text(ocr_result["text"], encoding="utf-8")

                derived_surface_entries.append(
                    {
                        "surface_id": surface_spec["surface_id"],
                        "source_pdf_page": page_number,
                        "surface_role": surface_spec["surface_role"],
                        "surface_order": surface_spec["surface_order"],
                        "source_spread_png_path": _relative_path(png_path, run_root),
                        "derived_png_path": _relative_path(derived_png_path, run_root),
                        "operation": surface_spec["operation"],
                        "crop_box_px": crop_box,
                        "image_size_px": {
                            "width": derived_image.width,
                            "height": derived_image.height,
                        },
                    }
                )

                stage1_entries.append(
                    {
                        "surface_id": surface_spec["surface_id"],
                        "source_pdf_page": page_number,
                        "surface_role": surface_spec["surface_role"],
                        "surface_order": surface_spec["surface_order"],
                        "source_spread_png_path": _relative_path(png_path, run_root),
                        "derived_png_path": _relative_path(derived_png_path, run_root),
                        "ocr_text_path": _relative_path(text_path, run_root),
                        "operation": surface_spec["operation"],
                        "crop_box_px": crop_box,
                        "image_size_px": {
                            "width": derived_image.width,
                            "height": derived_image.height,
                        },
                        "ocr_text_length": len(ocr_result["text"]),
                        "ocr_confidence_mean": ocr_result["confidence_mean"],
                        "ocr_confidence_sample_count": ocr_result["confidence_sample_count"],
                    }
                )
    finally:
        if hasattr(document, "close"):
            document.close()

    prep_manifest = {
        "command": "stage1-visual-extract",
        "scope": "prep-only retained evidence for stage-1 proof runs",
        "pdf_input": str(pdf_input),
        "page_range": page_range_spec,
        "selected_pages": selected_pages,
        "scan_layout": scan_layout,
        "spread_handling": resolved_spread_handling,
        "preprocess_controls": preprocess_controls,
        "generated_at_utc": _utc_now(),
        "rendered_pages": prep_entries,
        "derived_surfaces": derived_surface_entries,
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
        "spread_handling": resolved_spread_handling,
        "preprocess_controls": preprocess_controls,
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
        "derived_surface_count": len(stage1_entries),
        "spread_handling": resolved_spread_handling,
        "tesseract_path": discovery["selected_path"],
    }


def _build_surface_specs(
    pdf_page: int,
    page_width: int,
    page_height: int,
    width_padding: int,
    spread_handling: str,
    outer_crop_px: int,
    gutter_crop_px: int,
    top_crop_px: int,
    bottom_crop_px: int,
) -> list[dict[str, object]]:
    if spread_handling == "keep-whole":
        crop_box = _validated_crop_box(
            left=outer_crop_px,
            top=top_crop_px,
            right=page_width - outer_crop_px,
            bottom=page_height - bottom_crop_px,
            page_width=page_width,
            page_height=page_height,
            surface_label=f"PDF page {pdf_page}",
        )
        return [
            {
                "surface_id": f"pdf-page-{pdf_page:0{width_padding}d}-whole",
                "surface_role": "whole-spread",
                "surface_order": 0,
                "operation": "keep-whole",
                "crop_box_px": crop_box,
            }
        ]

    if spread_handling != "split-halves":
        raise CliError(f"unsupported spread handling mode: {spread_handling}")

    midpoint = page_width // 2
    left_box = _validated_crop_box(
        left=outer_crop_px,
        top=top_crop_px,
        right=midpoint - gutter_crop_px,
        bottom=page_height - bottom_crop_px,
        page_width=page_width,
        page_height=page_height,
        surface_label=f"PDF page {pdf_page} left surface",
    )
    right_box = _validated_crop_box(
        left=midpoint + gutter_crop_px,
        top=top_crop_px,
        right=page_width - outer_crop_px,
        bottom=page_height - bottom_crop_px,
        page_width=page_width,
        page_height=page_height,
        surface_label=f"PDF page {pdf_page} right surface",
    )
    return [
        {
            "surface_id": f"pdf-page-{pdf_page:0{width_padding}d}-left",
            "surface_role": "left-page",
            "surface_order": 0,
            "operation": "split-halves",
            "crop_box_px": left_box,
        },
        {
            "surface_id": f"pdf-page-{pdf_page:0{width_padding}d}-right",
            "surface_role": "right-page",
            "surface_order": 1,
            "operation": "split-halves",
            "crop_box_px": right_box,
        },
    ]


def _resolve_spread_handling(scan_layout: str, requested: str) -> str:
    if requested != "auto":
        return requested

    if scan_layout.strip().lower() == "two-page-spreads":
        return "split-halves"

    return "keep-whole"


def _run_ocr(image: object) -> dict[str, object]:
    text = pytesseract.image_to_string(image)
    confidence_mean = None
    confidence_sample_count = 0

    try:
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        confidences = []
        for raw_confidence in ocr_data.get("conf", []):
            try:
                confidence = float(raw_confidence)
            except (TypeError, ValueError):
                continue
            if confidence >= 0:
                confidences.append(confidence)

        if confidences:
            confidence_sample_count = len(confidences)
            confidence_mean = round(sum(confidences) / confidence_sample_count, 2)
    except pytesseract.TesseractError:
        confidence_mean = None
        confidence_sample_count = 0

    return {
        "text": text,
        "confidence_mean": confidence_mean,
        "confidence_sample_count": confidence_sample_count,
    }


def _validated_crop_box(
    left: int,
    top: int,
    right: int,
    bottom: int,
    page_width: int,
    page_height: int,
    surface_label: str,
) -> dict[str, int]:
    if left < 0 or top < 0 or right > page_width or bottom > page_height:
        raise CliError(f"crop box for {surface_label} falls outside the rasterized image bounds")
    if right <= left or bottom <= top:
        raise CliError(f"crop box for {surface_label} is empty after applying spread controls")
    return {
        "left": left,
        "top": top,
        "right": right,
        "bottom": bottom,
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