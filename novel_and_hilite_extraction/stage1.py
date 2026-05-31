from __future__ import annotations

from collections import defaultdict
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
import pypdfium2 as pdfium
import pytesseract


_OCR_TEXT_PLANE_STEPS = [
    "wash-out-colored-annotation-ink",
    "contrast-normalize-grayscale",
    "median-denoise",
]
_ENABLE_OCR_TEXT_PLANE_EXPERIMENT = False


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
    spread_rotation_deg: int | None,
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
    resolved_spread_rotation_deg = _resolve_spread_rotation_deg(scan_layout, spread_rotation_deg)
    ocr_text_plane_enabled = _ENABLE_OCR_TEXT_PLANE_EXPERIMENT

    run_root = output_root / run_label
    prep_dir = run_root / "prep" / "pdf-to-png"
    derived_dir = run_root / "prep" / "derived-surfaces"
    stage1_dir = run_root / "stage-1-visual-extraction"
    ocr_anchor_dir = stage1_dir / "ocr-anchors"
    annotation_dir = stage1_dir / "annotation-observables"
    ocr_text_plane_dir = stage1_dir / "ocr-text-planes" if ocr_text_plane_enabled else None
    prep_dir.mkdir(parents=True, exist_ok=False)
    derived_dir.mkdir(parents=True, exist_ok=False)
    stage1_dir.mkdir(parents=True, exist_ok=False)
    ocr_anchor_dir.mkdir(parents=True, exist_ok=False)
    annotation_dir.mkdir(parents=True, exist_ok=False)
    if ocr_text_plane_dir is not None:
        ocr_text_plane_dir.mkdir(parents=True, exist_ok=False)

    preprocess_controls = {
        "scan_layout": scan_layout,
        "requested_spread_handling": spread_handling,
        "resolved_spread_handling": resolved_spread_handling,
        "requested_spread_rotation_deg": spread_rotation_deg,
        "applied_spread_rotation_deg": resolved_spread_rotation_deg,
        "spread_rotation_defaulted": spread_rotation_deg is None,
        "spread_rotation_direction": "clockwise",
        "dpi": dpi,
        "outer_crop_px": outer_crop_px,
        "gutter_crop_px": gutter_crop_px,
        "top_crop_px": top_crop_px,
        "bottom_crop_px": bottom_crop_px,
        "ocr_text_plane": {
            "enabled": ocr_text_plane_enabled,
            "shared_geometry_with_derived_surface": ocr_text_plane_enabled,
            "steps": _OCR_TEXT_PLANE_STEPS if ocr_text_plane_enabled else [],
        },
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
                raw_image = bitmap.to_pil()
            finally:
                if hasattr(page, "close"):
                    page.close()

            png_name = f"pdf-page-{page_number:0{width}d}.png"
            raw_png_path = prep_dir / png_name
            raw_image.save(raw_png_path, format="PNG")

            rectified_png_path = None
            source_image = raw_image
            if resolved_spread_rotation_deg:
                source_image = raw_image.rotate(-resolved_spread_rotation_deg, expand=True)
                rectified_png_path = prep_dir / f"pdf-page-{page_number:0{width}d}-rectified.png"
                source_image.save(rectified_png_path, format="PNG")

            raw_png_relative_path = _relative_path(raw_png_path, run_root)
            source_png_path = rectified_png_path or raw_png_path
            source_png_relative_path = _relative_path(source_png_path, run_root)
            rectified_png_relative_path = (
                _relative_path(rectified_png_path, run_root)
                if rectified_png_path is not None
                else None
            )

            surface_specs = _build_surface_specs(
                pdf_page=page_number,
                page_width=source_image.width,
                page_height=source_image.height,
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
                    "png_path": raw_png_relative_path,
                    "raw_spread_png_path": raw_png_relative_path,
                    "rectified_spread_png_path": rectified_png_relative_path,
                    "source_spread_png_path": source_png_relative_path,
                    "image_size_px": {"width": raw_image.width, "height": raw_image.height},
                    "source_image_size_px": {
                        "width": source_image.width,
                        "height": source_image.height,
                    },
                    "requested_spread_rotation_deg": spread_rotation_deg,
                    "applied_spread_rotation_deg": resolved_spread_rotation_deg,
                    "spread_rotation_defaulted": spread_rotation_deg is None,
                    "spread_rotation_direction": "clockwise",
                    "derived_surface_ids": [surface_spec["surface_id"] for surface_spec in surface_specs],
                }
            )

            for surface_spec in surface_specs:
                crop_box = surface_spec["crop_box_px"]
                derived_image = source_image.crop(
                    (
                        crop_box["left"],
                        crop_box["top"],
                        crop_box["right"],
                        crop_box["bottom"],
                    )
                )
                derived_png_path = derived_dir / f"{surface_spec['surface_id']}.png"
                derived_image.save(derived_png_path, format="PNG")

                ocr_text_plane = None
                ocr_text_plane_path = None
                ocr_input_image = derived_image
                if ocr_text_plane_dir is not None:
                    ocr_text_plane = _build_ocr_text_plane(derived_image)
                    ocr_text_plane_path = (
                        ocr_text_plane_dir / f"{surface_spec['surface_id']}-ocr-text-plane.png"
                    )
                    cv2.imwrite(str(ocr_text_plane_path), ocr_text_plane["image"])
                    ocr_input_image = ocr_text_plane["image"]

                ocr_result = _run_ocr(ocr_input_image)
                text_path = stage1_dir / f"{surface_spec['surface_id']}.txt"
                text_path.write_text(ocr_result["text"], encoding="utf-8")
                ocr_anchor_path = ocr_anchor_dir / f"{surface_spec['surface_id']}-ocr-anchors.json"
                annotation_mask_path = annotation_dir / f"{surface_spec['surface_id']}-mark-mask.png"
                annotation_candidate_path = (
                    annotation_dir / f"{surface_spec['surface_id']}-mark-candidates.json"
                )
                annotation_observables = _build_annotation_observables(
                    image=derived_image,
                    word_anchors=ocr_result["word_anchors"],
                    line_anchors=ocr_result["line_anchors"],
                )
                _write_json(
                    ocr_anchor_path,
                    {
                        "surface_id": surface_spec["surface_id"],
                        "word_anchors": ocr_result["word_anchors"],
                        "line_anchors": ocr_result["line_anchors"],
                    },
                )
                cv2.imwrite(
                    str(annotation_mask_path),
                    annotation_observables["mark_mask_image"],
                )
                _write_json(
                    annotation_candidate_path,
                    {
                        "surface_id": surface_spec["surface_id"],
                        "normalized_class_set": sorted(
                            {
                                candidate["normalized_class"]
                                for candidate in annotation_observables["mark_candidates"]
                            }
                        ),
                        "mark_candidates": annotation_observables["mark_candidates"],
                        "anchor_relations": annotation_observables["anchor_relations"],
                    },
                )

                derived_surface_entries.append(
                    {
                        "surface_id": surface_spec["surface_id"],
                        "source_pdf_page": page_number,
                        "surface_role": surface_spec["surface_role"],
                        "surface_order": surface_spec["surface_order"],
                        "raw_spread_png_path": raw_png_relative_path,
                        "rectified_spread_png_path": rectified_png_relative_path,
                        "source_spread_png_path": source_png_relative_path,
                        "derived_png_path": _relative_path(derived_png_path, run_root),
                        "source_spread_rotation_deg": resolved_spread_rotation_deg,
                        "source_spread_rotation_defaulted": spread_rotation_deg is None,
                        "source_spread_rotation_direction": "clockwise",
                        "operation": surface_spec["operation"],
                        "crop_box_px": crop_box,
                        "image_size_px": {
                            "width": derived_image.width,
                            "height": derived_image.height,
                        },
                    }
                )
                if ocr_text_plane_path is not None and ocr_text_plane is not None:
                    derived_surface_entries[-1]["ocr_text_plane_png_path"] = _relative_path(
                        ocr_text_plane_path,
                        run_root,
                    )
                    derived_surface_entries[-1][
                        "ocr_text_plane_shared_geometry_with_derived_surface"
                    ] = True
                    derived_surface_entries[-1]["ocr_text_plane_preprocess"] = ocr_text_plane[
                        "preprocess"
                    ]

                stage1_entries.append(
                    {
                        "surface_id": surface_spec["surface_id"],
                        "source_pdf_page": page_number,
                        "surface_role": surface_spec["surface_role"],
                        "surface_order": surface_spec["surface_order"],
                        "raw_spread_png_path": raw_png_relative_path,
                        "rectified_spread_png_path": rectified_png_relative_path,
                        "source_spread_png_path": source_png_relative_path,
                        "derived_png_path": _relative_path(derived_png_path, run_root),
                        "ocr_text_path": _relative_path(text_path, run_root),
                        "source_spread_rotation_deg": resolved_spread_rotation_deg,
                        "source_spread_rotation_defaulted": spread_rotation_deg is None,
                        "source_spread_rotation_direction": "clockwise",
                        "operation": surface_spec["operation"],
                        "crop_box_px": crop_box,
                        "image_size_px": {
                            "width": derived_image.width,
                            "height": derived_image.height,
                        },
                        "ocr_text_length": len(ocr_result["text"]),
                        "ocr_confidence_mean": ocr_result["confidence_mean"],
                        "ocr_confidence_sample_count": ocr_result["confidence_sample_count"],
                        "ocr_anchor_json_path": _relative_path(ocr_anchor_path, run_root),
                        "annotation_mark_mask_path": _relative_path(annotation_mask_path, run_root),
                        "annotation_mark_candidates_path": _relative_path(
                            annotation_candidate_path,
                            run_root,
                        ),
                        "ocr_word_anchor_count": len(ocr_result["word_anchors"]),
                        "ocr_line_anchor_count": len(ocr_result["line_anchors"]),
                        "annotation_candidate_count": len(
                            annotation_observables["mark_candidates"]
                        ),
                        "annotation_confident_candidate_count": annotation_observables[
                            "confident_candidate_count"
                        ],
                        "annotation_candidate_class_counts": annotation_observables[
                            "candidate_class_counts"
                        ],
                    }
                )
                if ocr_text_plane_path is not None and ocr_text_plane is not None:
                    stage1_entries[-1]["ocr_text_plane_png_path"] = _relative_path(
                        ocr_text_plane_path,
                        run_root,
                    )
                    stage1_entries[-1][
                        "ocr_text_plane_shared_geometry_with_derived_surface"
                    ] = True
                    stage1_entries[-1]["ocr_text_plane_preprocess"] = ocr_text_plane[
                        "preprocess"
                    ]
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
        "annotation_observables_note": (
            "Stage 1 retains OCR anchor geometry, visual mark candidates, and geometric candidate-to-anchor "
            "relations only. It does not resolve text spans, interpret markings, or synthesize artifact entries."
        ),
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
    if ocr_text_plane_enabled:
        stage1_manifest["ocr_text_plane_note"] = (
            "Stage 1 OCR runs on a retained sibling text plane derived from each derived surface. "
            "Annotation masks and mark candidates remain computed on the original derived surface."
        )
    _write_json(stage1_dir / "manifest.json", stage1_manifest)

    return {
        "run_root": str(run_root),
        "prep_manifest": str(prep_dir / "manifest.json"),
        "stage1_manifest": str(stage1_dir / "manifest.json"),
        "selected_pages": selected_pages,
        "derived_surface_count": len(stage1_entries),
        "annotation_candidate_count": sum(
            int(entry["annotation_candidate_count"]) for entry in stage1_entries
        ),
        "annotation_confident_candidate_count": sum(
            int(entry["annotation_confident_candidate_count"]) for entry in stage1_entries
        ),
        "spread_handling": resolved_spread_handling,
        "applied_spread_rotation_deg": resolved_spread_rotation_deg,
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


def _resolve_spread_rotation_deg(scan_layout: str, requested: int | None) -> int:
    if requested is not None:
        if requested not in {0, 90, 180, 270}:
            raise CliError("--spread-rotation-deg must be one of 0, 90, 180, or 270")
        return requested

    if scan_layout.strip().lower() == "two-page-spreads":
        return 90

    return 0


def _build_ocr_text_plane(image: object) -> dict[str, object]:
    rgb_image = np.array(image.convert("RGB"), dtype=np.uint8)
    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)

    color_mask = (hsv_image[:, :, 1] >= 35) & (hsv_image[:, :, 2] >= 80)
    washed_gray = gray_image.copy()
    washed_gray[color_mask] = 255

    normalized_gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(washed_gray)
    denoised_gray = cv2.medianBlur(normalized_gray, 3)

    return {
        "image": denoised_gray,
        "preprocess": {
            "shared_geometry_with_derived_surface": True,
            "steps": _OCR_TEXT_PLANE_STEPS,
            "color_suppression_saturation_min": 35,
            "color_suppression_value_min": 80,
            "suppressed_color_pixel_count": int(np.count_nonzero(color_mask)),
            "contrast_normalization": {
                "method": "clahe",
                "clip_limit": 2.0,
                "tile_grid_size": [8, 8],
            },
            "denoise": {
                "method": "median-blur",
                "kernel_size": 3,
            },
        },
    }


def _run_ocr(image: object) -> dict[str, object]:
    text = pytesseract.image_to_string(image)
    confidence_mean = None
    confidence_sample_count = 0
    word_anchors: list[dict[str, object]] = []
    line_anchors: list[dict[str, object]] = []

    try:
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        word_anchors, line_anchors = _build_ocr_anchor_tables(ocr_data)
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
        "word_anchors": word_anchors,
        "line_anchors": line_anchors,
    }


def _build_ocr_anchor_tables(
    ocr_data: dict[str, list[object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    total_rows = len(ocr_data.get("text", []))
    word_anchors: list[dict[str, object]] = []
    line_groups: dict[tuple[int, int, int, int], dict[str, object]] = {}

    for index in range(total_rows):
        text = str(ocr_data.get("text", [""])[index] or "").strip()
        width = _safe_int(ocr_data, "width", index)
        height = _safe_int(ocr_data, "height", index)
        if not text or width <= 0 or height <= 0:
            continue

        left = _safe_int(ocr_data, "left", index)
        top = _safe_int(ocr_data, "top", index)
        confidence = _safe_float(ocr_data.get("conf", []), index)
        page_num = max(1, _safe_int(ocr_data, "page_num", index, fallback=1))
        block_num = _safe_int(ocr_data, "block_num", index, fallback=0)
        par_num = _safe_int(ocr_data, "par_num", index, fallback=0)
        line_num = _safe_int(ocr_data, "line_num", index, fallback=0)
        word_num = _safe_int(ocr_data, "word_num", index, fallback=0)
        line_key = (page_num, block_num, par_num, line_num)
        line_id = (
            f"ocr-line-{page_num:02d}-{block_num:02d}-{par_num:02d}-{line_num:02d}"
        )
        word_id = (
            f"ocr-word-{page_num:02d}-{block_num:02d}-{par_num:02d}-{line_num:02d}-{word_num:02d}"
        )
        bbox = _bbox_from_left_top_width_height(left, top, width, height)
        word_anchor = {
            "ocr_word_id": word_id,
            "ocr_line_id": line_id,
            "text": text,
            "confidence": confidence,
            "bbox_px": bbox,
            "reading_order": len(word_anchors) + 1,
            "hierarchy": {
                "page_num": page_num,
                "block_num": block_num,
                "par_num": par_num,
                "line_num": line_num,
                "word_num": word_num,
            },
        }
        word_anchors.append(word_anchor)

        line_group = line_groups.setdefault(
            line_key,
            {
                "ocr_line_id": line_id,
                "word_ids": [],
                "words": [],
                "confidences": [],
                "left": bbox["left"],
                "top": bbox["top"],
                "right": bbox["right"],
                "bottom": bbox["bottom"],
                "reading_order": len(line_groups) + 1,
            },
        )
        line_group["word_ids"].append(word_id)
        line_group["words"].append(text)
        if confidence is not None and confidence >= 0:
            line_group["confidences"].append(confidence)
        line_group["left"] = min(line_group["left"], bbox["left"])
        line_group["top"] = min(line_group["top"], bbox["top"])
        line_group["right"] = max(line_group["right"], bbox["right"])
        line_group["bottom"] = max(line_group["bottom"], bbox["bottom"])

    line_anchors: list[dict[str, object]] = []
    for line_group in sorted(line_groups.values(), key=lambda item: item["reading_order"]):
        line_confidences = line_group.pop("confidences")
        line_anchors.append(
            {
                "ocr_line_id": line_group["ocr_line_id"],
                "word_ids": line_group["word_ids"],
                "text": " ".join(line_group["words"]),
                "confidence_mean": (
                    round(sum(line_confidences) / len(line_confidences), 2)
                    if line_confidences
                    else None
                ),
                "bbox_px": {
                    "left": line_group["left"],
                    "top": line_group["top"],
                    "right": line_group["right"],
                    "bottom": line_group["bottom"],
                    "width": line_group["right"] - line_group["left"],
                    "height": line_group["bottom"] - line_group["top"],
                },
                "reading_order": line_group["reading_order"],
            }
        )

    return word_anchors, line_anchors


def _build_annotation_observables(
    image: object,
    word_anchors: list[dict[str, object]],
    line_anchors: list[dict[str, object]],
) -> dict[str, object]:
    rgb_image = np.array(image.convert("RGB"), dtype=np.uint8)
    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
    height, width = gray_image.shape
    text_mask = _build_text_anchor_mask(width, height, word_anchors)

    color_mask = (hsv_image[:, :, 1] >= 35) & (hsv_image[:, :, 2] >= 80)
    color_mask = _clean_binary_mask(color_mask, open_kernel=(2, 2), close_kernel=(7, 7))

    dark_mask = (gray_image <= 145) & (~text_mask)
    dark_mask = _clean_binary_mask(dark_mask, open_kernel=(2, 2), close_kernel=(3, 3))
    dark_mask = _suppress_border_band(dark_mask, band_size=8)

    combined_mask = color_mask | dark_mask
    mask_image = combined_mask.astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contour_rows: list[tuple[int, int, int, np.ndarray]] = []
    for contour in contours:
        area = int(round(cv2.contourArea(contour)))
        if area < 80:
            continue
        x, y, contour_width, contour_height = cv2.boundingRect(contour)
        contour_rows.append((y, x, area, contour))

    contour_rows.sort(key=lambda row: (row[0], row[1], -row[2]))
    mark_candidates: list[dict[str, object]] = []
    anchor_relations: list[dict[str, object]] = []
    candidate_class_counts: dict[str, int] = defaultdict(int)
    confident_candidate_count = 0

    for candidate_index, (_, _, _, contour) in enumerate(contour_rows, start=1):
        x, y, contour_width, contour_height = cv2.boundingRect(contour)
        contour_mask = np.zeros_like(mask_image, dtype=np.uint8)
        cv2.drawContours(contour_mask, [contour], contourIdx=-1, color=255, thickness=-1)
        candidate_pixels = contour_mask > 0
        candidate_pixel_count = int(np.count_nonzero(candidate_pixels))
        colored_pixel_count = int(np.count_nonzero(candidate_pixels & color_mask))
        dark_pixel_count = int(np.count_nonzero(candidate_pixels & dark_mask))
        candidate_bbox = _bbox_from_left_top_width_height(x, y, contour_width, contour_height)
        if _should_skip_candidate_artifact(
            candidate_bbox=candidate_bbox,
            candidate_pixel_count=candidate_pixel_count,
            colored_pixel_count=colored_pixel_count,
            page_width=width,
            page_height=height,
        ):
            continue
        relation_rows = _candidate_anchor_relations(
            candidate_index=candidate_index,
            candidate_bbox=candidate_bbox,
            page_width=width,
            page_height=height,
            word_anchors=word_anchors,
            line_anchors=line_anchors,
        )
        classification = _classify_mark_candidate(
            candidate_bbox=candidate_bbox,
            candidate_pixel_count=candidate_pixel_count,
            colored_pixel_count=colored_pixel_count,
            dark_pixel_count=dark_pixel_count,
            relation_rows=relation_rows,
            page_width=width,
            page_height=height,
        )
        candidate_id = f"mark-candidate-{candidate_index:04d}"
        for relation_row in relation_rows:
            relation_row["candidate_id"] = candidate_id
        anchor_relations.extend(relation_rows)

        candidate = {
            "candidate_id": candidate_id,
            "bbox_px": candidate_bbox,
            "pixel_area": candidate_pixel_count,
            "contour_area": int(round(cv2.contourArea(contour))),
            "fill_ratio": round(
                candidate_pixel_count / max(1, candidate_bbox["width"] * candidate_bbox["height"]),
                3,
            ),
            "aspect_ratio": round(
                max(contour_width, contour_height) / max(1, min(contour_width, contour_height)),
                2,
            ),
            "ink_summary": {
                "colored_pixel_count": colored_pixel_count,
                "dark_pixel_count": dark_pixel_count,
                "colored_pixel_ratio": round(colored_pixel_count / max(1, candidate_pixel_count), 3),
                "dark_pixel_ratio": round(dark_pixel_count / max(1, candidate_pixel_count), 3),
            },
            "raw_visible_mark_label": classification["raw_visible_mark_label"],
            "normalized_class": classification["normalized_class"],
            "detection_confidence": classification["detection_confidence"],
            "uncertainty_flags": classification["uncertainty_flags"],
            "linked_ocr_word_ids": sorted(
                {
                    relation_row["anchor_id"]
                    for relation_row in relation_rows
                    if relation_row["anchor_type"] == "ocr-word"
                }
            ),
            "linked_ocr_line_ids": sorted(
                {
                    relation_row["anchor_id"]
                    for relation_row in relation_rows
                    if relation_row["anchor_type"] == "ocr-line"
                }
            ),
            "relation_types": sorted({relation_row["relation_type"] for relation_row in relation_rows}),
        }
        mark_candidates.append(candidate)

    _apply_surface_uncertainty_overrides(mark_candidates, page_width=width, page_height=height)

    for candidate in mark_candidates:
        candidate_class_counts[candidate["normalized_class"]] += 1
        if candidate["detection_confidence"] >= 0.6 and not candidate["uncertainty_flags"]:
            confident_candidate_count += 1

    return {
        "mark_mask_image": mask_image,
        "mark_candidates": mark_candidates,
        "anchor_relations": anchor_relations,
        "candidate_class_counts": dict(sorted(candidate_class_counts.items())),
        "confident_candidate_count": confident_candidate_count,
    }


def _build_text_anchor_mask(
    image_width: int,
    image_height: int,
    word_anchors: list[dict[str, object]],
) -> np.ndarray:
    text_mask = np.zeros((image_height, image_width), dtype=np.uint8)
    for word_anchor in word_anchors:
        bbox = word_anchor["bbox_px"]
        left = max(0, int(bbox["left"]) - 3)
        top = max(0, int(bbox["top"]) - 2)
        right = min(image_width, int(bbox["right"]) + 3)
        bottom = min(image_height, int(bbox["bottom"]) + 2)
        text_mask[top:bottom, left:right] = 255
    return text_mask > 0


def _clean_binary_mask(
    binary_mask: np.ndarray,
    open_kernel: tuple[int, int],
    close_kernel: tuple[int, int],
) -> np.ndarray:
    uint_mask = binary_mask.astype(np.uint8) * 255
    open_struct = cv2.getStructuringElement(cv2.MORPH_RECT, open_kernel)
    close_struct = cv2.getStructuringElement(cv2.MORPH_RECT, close_kernel)
    opened = cv2.morphologyEx(uint_mask, cv2.MORPH_OPEN, open_struct)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, close_struct)
    return closed > 0


def _suppress_border_band(binary_mask: np.ndarray, band_size: int) -> np.ndarray:
    suppressed = binary_mask.copy()
    if band_size <= 0:
        return suppressed
    suppressed[:band_size, :] = False
    suppressed[-band_size:, :] = False
    suppressed[:, :band_size] = False
    suppressed[:, -band_size:] = False
    return suppressed


def _candidate_anchor_relations(
    candidate_index: int,
    candidate_bbox: dict[str, int],
    page_width: int,
    page_height: int,
    word_anchors: list[dict[str, object]],
    line_anchors: list[dict[str, object]],
) -> list[dict[str, object]]:
    relations: list[dict[str, object]] = []
    candidate_left = candidate_bbox["left"]
    candidate_top = candidate_bbox["top"]
    candidate_right = candidate_bbox["right"]
    margin_threshold = max(20, int(page_width * 0.12))

    for word_anchor in word_anchors:
        word_bbox = word_anchor["bbox_px"]
        overlap_area = _intersection_area(candidate_bbox, word_bbox)
        horizontal_overlap = _horizontal_overlap_ratio(candidate_bbox, word_bbox)
        vertical_gap = _vertical_gap(candidate_bbox, word_bbox)
        if overlap_area > 0:
            relation_type = "overlaps-text"
        elif (
            candidate_top >= word_bbox["bottom"] - max(4, int(word_bbox["height"] * 0.25))
            and candidate_top <= word_bbox["bottom"] + word_bbox["height"]
            and horizontal_overlap >= 0.5
            and candidate_bbox["width"] >= max(20, word_bbox["width"] // 2)
        ):
            relation_type = "below-text"
        else:
            continue
        relations.append(
            {
                "candidate_id": f"mark-candidate-{candidate_index:04d}",
                "anchor_type": "ocr-word",
                "anchor_id": word_anchor["ocr_word_id"],
                "relation_type": relation_type,
                "overlap_area_px": overlap_area,
                "distance_px": vertical_gap,
                "ambiguous": False,
            }
        )

    for line_anchor in line_anchors:
        line_bbox = line_anchor["bbox_px"]
        overlap_area = _intersection_area(candidate_bbox, line_bbox)
        horizontal_overlap = _horizontal_overlap_ratio(candidate_bbox, line_bbox)
        line_margin = max(12, int(line_bbox["height"] * 0.6))
        if _bbox_encloses(candidate_bbox, line_bbox, padding=line_margin):
            relation_type = "encloses-text-region"
        elif overlap_area > 0:
            relation_type = "overlaps-text"
        elif (
            candidate_top >= line_bbox["bottom"] - max(4, int(line_bbox["height"] * 0.3))
            and candidate_top <= line_bbox["bottom"] + line_bbox["height"]
            and horizontal_overlap >= 0.5
            and candidate_bbox["width"] >= max(30, line_bbox["width"] // 3)
            and candidate_bbox["height"] <= max(30, int(line_bbox["height"] * 1.6))
        ):
            relation_type = "below-text"
        elif (
            _bbox_distance(candidate_bbox, line_bbox) <= max(30, int(line_bbox["height"] * 2.5))
            and (
                candidate_left <= margin_threshold
                or candidate_right >= page_width - margin_threshold
                or candidate_top <= max(40, int(page_height * 0.08))
            )
        ):
            relation_type = "marginal-adjacent"
        else:
            continue
        relations.append(
            {
                "candidate_id": f"mark-candidate-{candidate_index:04d}",
                "anchor_type": "ocr-line",
                "anchor_id": line_anchor["ocr_line_id"],
                "relation_type": relation_type,
                "overlap_area_px": overlap_area,
                "distance_px": _bbox_distance(candidate_bbox, line_bbox),
                "ambiguous": False,
            }
        )

    relation_types = {relation["relation_type"] for relation in relations}
    if len(relation_types) > 1 and relation_types != {"below-text", "overlaps-text"}:
        for relation in relations:
            relation["ambiguous"] = True

    return relations


def _classify_mark_candidate(
    candidate_bbox: dict[str, int],
    candidate_pixel_count: int,
    colored_pixel_count: int,
    dark_pixel_count: int,
    relation_rows: list[dict[str, object]],
    page_width: int,
    page_height: int,
) -> dict[str, object]:
    candidate_width = candidate_bbox["width"]
    candidate_height = candidate_bbox["height"]
    colored_ratio = colored_pixel_count / max(1, candidate_pixel_count)
    dark_ratio = dark_pixel_count / max(1, candidate_pixel_count)
    relation_types = {relation_row["relation_type"] for relation_row in relation_rows}
    touches_edge = (
        candidate_bbox["left"] <= 8
        or candidate_bbox["top"] <= 8
        or candidate_bbox["right"] >= page_width - 8
        or candidate_bbox["bottom"] >= page_height - 8
    )
    shape_aspect_ratio = max(candidate_width, candidate_height) / max(1, min(candidate_width, candidate_height))
    note_like_shape = (
        candidate_width >= 14
        and candidate_height <= 120
        and shape_aspect_ratio <= 4.0
    )
    uncertainty_flags: list[str] = []
    if touches_edge:
        uncertainty_flags.append("touches-surface-edge")
    if not relation_rows:
        uncertainty_flags.append("no-ocr-anchor")
    if len(relation_types) > 1:
        uncertainty_flags.append("ambiguous-anchor")
    if colored_ratio > 0.15 and dark_ratio > 0.15:
        uncertainty_flags.append("mixed-ink-signature")

    normalized_class = "unknown"
    raw_visible_mark_label = "unclassified-mark"
    detection_confidence = 0.35

    if (
        "encloses-text-region" in relation_types
        and candidate_height >= 20
        and (not touches_edge or colored_ratio >= 0.2)
    ):
        normalized_class = "bracket-or-box"
        raw_visible_mark_label = "enclosure-stroke"
        detection_confidence = 0.8 if colored_ratio >= 0.2 or dark_ratio >= 0.3 else 0.65
    elif "below-text" in relation_types and candidate_width >= max(40, candidate_height * 2):
        normalized_class = "underline"
        raw_visible_mark_label = "underline-stroke"
        detection_confidence = 0.78 if colored_ratio >= 0.2 else 0.62
    elif "overlaps-text" in relation_types and colored_ratio >= 0.2:
        normalized_class = "highlight"
        raw_visible_mark_label = "colored-text-overlap"
        detection_confidence = 0.82 if candidate_width >= 40 else 0.68
    elif (
        dark_ratio >= 0.35
        and candidate_width <= int(page_width * 0.35)
        and candidate_height <= int(page_height * 0.25)
        and note_like_shape
        and not touches_edge
        and ("marginal-adjacent" in relation_types or "no-ocr-anchor" in uncertainty_flags)
    ):
        normalized_class = "marginalia"
        raw_visible_mark_label = "dark-freehand-mark"
        detection_confidence = 0.72

    if normalized_class == "unknown":
        uncertainty_flags.append("unknown-mark-form")
    if detection_confidence < 0.6:
        uncertainty_flags.append("low-mark-confidence")

    return {
        "raw_visible_mark_label": raw_visible_mark_label,
        "normalized_class": normalized_class,
        "detection_confidence": round(detection_confidence, 2),
        "uncertainty_flags": sorted(set(uncertainty_flags)),
    }


def _apply_surface_uncertainty_overrides(
    mark_candidates: list[dict[str, object]],
    page_width: int,
    page_height: int,
) -> None:
    margin_noise_candidates: list[dict[str, object]] = []
    margin_limit = max(70, int(page_width * 0.08))
    band_height = max(1, page_height // 6)

    for candidate in mark_candidates:
        if candidate["normalized_class"] != "marginalia":
            continue
        bbox = candidate["bbox_px"]
        if bbox["left"] > margin_limit:
            continue
        if bbox["width"] > 30 or bbox["height"] > 45:
            continue
        if "marginal-adjacent" not in candidate["relation_types"] and "no-ocr-anchor" not in candidate["uncertainty_flags"]:
            continue
        margin_noise_candidates.append(candidate)

    vertical_bands = {
        int(candidate["bbox_px"]["top"]) // band_height for candidate in margin_noise_candidates
    }
    if len(margin_noise_candidates) < 4 or len(vertical_bands) < 3:
        return

    for candidate in margin_noise_candidates:
        uncertainty_flags = set(candidate["uncertainty_flags"])
        uncertainty_flags.add("dense-margin-dark-noise")
        candidate["uncertainty_flags"] = sorted(uncertainty_flags)


def _should_skip_candidate_artifact(
    candidate_bbox: dict[str, int],
    candidate_pixel_count: int,
    colored_pixel_count: int,
    page_width: int,
    page_height: int,
) -> bool:
    touches_edge = (
        candidate_bbox["left"] <= 8
        or candidate_bbox["top"] <= 8
        or candidate_bbox["right"] >= page_width - 8
        or candidate_bbox["bottom"] >= page_height - 8
    )
    fill_ratio = candidate_pixel_count / max(1, candidate_bbox["width"] * candidate_bbox["height"])
    spans_surface = (
        candidate_bbox["width"] >= int(page_width * 0.9)
        and candidate_bbox["height"] >= int(page_height * 0.9)
    )
    spans_major_axis = (
        candidate_bbox["height"] >= int(page_height * 0.7)
        or candidate_bbox["width"] >= int(page_width * 0.7)
    )
    return (
        touches_edge
        and colored_pixel_count == 0
        and fill_ratio <= 0.18
        and (spans_surface or spans_major_axis)
    )


def _bbox_from_left_top_width_height(left: int, top: int, width: int, height: int) -> dict[str, int]:
    return {
        "left": left,
        "top": top,
        "right": left + width,
        "bottom": top + height,
        "width": width,
        "height": height,
    }


def _intersection_area(first_bbox: dict[str, int], second_bbox: dict[str, int]) -> int:
    overlap_left = max(first_bbox["left"], second_bbox["left"])
    overlap_top = max(first_bbox["top"], second_bbox["top"])
    overlap_right = min(first_bbox["right"], second_bbox["right"])
    overlap_bottom = min(first_bbox["bottom"], second_bbox["bottom"])
    overlap_width = max(0, overlap_right - overlap_left)
    overlap_height = max(0, overlap_bottom - overlap_top)
    return overlap_width * overlap_height


def _horizontal_overlap_ratio(first_bbox: dict[str, int], second_bbox: dict[str, int]) -> float:
    overlap_left = max(first_bbox["left"], second_bbox["left"])
    overlap_right = min(first_bbox["right"], second_bbox["right"])
    overlap_width = max(0, overlap_right - overlap_left)
    return overlap_width / max(1, min(first_bbox["width"], second_bbox["width"]))


def _vertical_gap(first_bbox: dict[str, int], second_bbox: dict[str, int]) -> int:
    if first_bbox["bottom"] < second_bbox["top"]:
        return second_bbox["top"] - first_bbox["bottom"]
    if second_bbox["bottom"] < first_bbox["top"]:
        return first_bbox["top"] - second_bbox["bottom"]
    return 0


def _bbox_distance(first_bbox: dict[str, int], second_bbox: dict[str, int]) -> int:
    horizontal_gap = 0
    vertical_gap = 0
    if first_bbox["right"] < second_bbox["left"]:
        horizontal_gap = second_bbox["left"] - first_bbox["right"]
    elif second_bbox["right"] < first_bbox["left"]:
        horizontal_gap = first_bbox["left"] - second_bbox["right"]
    if first_bbox["bottom"] < second_bbox["top"]:
        vertical_gap = second_bbox["top"] - first_bbox["bottom"]
    elif second_bbox["bottom"] < first_bbox["top"]:
        vertical_gap = first_bbox["top"] - second_bbox["bottom"]
    return int(round((horizontal_gap ** 2 + vertical_gap ** 2) ** 0.5))


def _bbox_encloses(
    outer_bbox: dict[str, int],
    inner_bbox: dict[str, int],
    padding: int,
) -> bool:
    return (
        outer_bbox["left"] <= inner_bbox["left"] - padding
        and outer_bbox["top"] <= inner_bbox["top"] - padding
        and outer_bbox["right"] >= inner_bbox["right"] + padding
        and outer_bbox["bottom"] >= inner_bbox["bottom"] + padding
    )


def _safe_int(
    ocr_data: dict[str, list[object]],
    key: str,
    index: int,
    fallback: int = 0,
) -> int:
    try:
        return int(ocr_data.get(key, [fallback])[index])
    except (ValueError, TypeError, IndexError):
        return fallback


def _safe_float(values: list[object], index: int) -> float | None:
    try:
        value = float(values[index])
    except (ValueError, TypeError, IndexError):
        return None
    if value < 0:
        return None
    return round(value, 2)


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