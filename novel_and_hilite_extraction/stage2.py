from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


class CliError(RuntimeError):
    pass


def run_stage2_structural_reconstruct(
    run_root: Path,
    reconstruction_scope: str,
) -> dict[str, object]:
    if not run_root.is_dir():
        raise CliError(f"run root does not exist: {run_root}")
    if reconstruction_scope not in {"page-units", "block-units"}:
        raise CliError(f"unsupported reconstruction scope: {reconstruction_scope}")

    stage1_manifest_path = run_root / "stage-1-visual-extraction" / "manifest.json"
    stage1_manifest = _read_json(stage1_manifest_path)
    ordered_entries = _validated_stage1_entries(
        stage1_manifest_path=stage1_manifest_path,
        stage1_manifest=stage1_manifest,
        run_root=run_root,
    )

    stage2_dir = run_root / "stage-2-structural-reconstruction"
    stage2_dir.mkdir(parents=True, exist_ok=False)

    selected_logical_page_order: list[dict[str, object]] = []
    logical_pages: list[dict[str, object]] = []
    block_units: list[dict[str, object]] = []

    for logical_page_order, entry in enumerate(ordered_entries, start=1):
        logical_page_id = f"logical-page-{logical_page_order:04d}"
        evidence_text_path = stage2_dir / f"{logical_page_id}.txt"
        evidence_text = entry["ocr_text_abs_path"].read_text(encoding="utf-8")
        evidence_text_path.write_text(
            evidence_text,
            encoding="utf-8",
        )
        evidence_text_path_relative = _relative_path(evidence_text_path, run_root)
        logical_page_uncertainty_flags = list(entry["uncertainty_flags"])

        selected_logical_page_order.append(
            {
                "logical_page_id": logical_page_id,
                "logical_page_order": logical_page_order,
                "source_pdf_page": entry["source_pdf_page"],
                "surface_order": entry["surface_order"],
                "surface_id": entry["surface_id"],
            }
        )
        logical_page_record = {
            "logical_page_id": logical_page_id,
            "logical_page_order": logical_page_order,
            "reconstruction_scope": reconstruction_scope,
            "evidence_text_path": evidence_text_path_relative,
            "ordering_basis": {
                "source_pdf_page": entry["source_pdf_page"],
                "surface_order": entry["surface_order"],
            },
            "lineage": {
                "source_pdf_page": entry["source_pdf_page"],
                "surface_id": entry["surface_id"],
                "surface_role": entry["surface_role"],
                "surface_order": entry["surface_order"],
                "source_spread_png_path": entry["source_spread_png_path"],
                "derived_png_path": entry["derived_png_path"],
                "stage1_ocr_text_path": entry["ocr_text_path"],
            },
            "upstream_ocr": {
                "ocr_text_length": entry["ocr_text_length"],
                "ocr_confidence_mean": entry["ocr_confidence_mean"],
                "ocr_confidence_sample_count": entry["ocr_confidence_sample_count"],
            },
            "uncertainty_flags": logical_page_uncertainty_flags,
        }

        if reconstruction_scope == "block-units":
            block_texts = _segment_ocr_text_into_blocks(evidence_text)
            logical_page_record["block_segmentation"] = {
                "basis": "consecutive-non-empty-lines-separated-by-blank-lines",
                "block_count": len(block_texts),
            }
            if not block_texts:
                logical_page_record["uncertainty_flags"] = [
                    *logical_page_uncertainty_flags,
                    "no-non-empty-ocr-lines",
                ]
            else:
                block_order_start = len(block_units) + 1
                for block_order_within_logical_page, block_text in enumerate(block_texts, start=1):
                    block_order = len(block_units) + 1
                    block_id = f"block-unit-{block_order:04d}"
                    block_evidence_text_path = stage2_dir / f"{block_id}.txt"
                    block_evidence_text_path.write_text(block_text, encoding="utf-8")
                    block_units.append(
                        {
                            "block_id": block_id,
                            "block_order": block_order,
                            "block_order_within_logical_page": block_order_within_logical_page,
                            "logical_page_id": logical_page_id,
                            "logical_page_order": logical_page_order,
                            "reconstruction_scope": reconstruction_scope,
                            "evidence_text_path": _relative_path(block_evidence_text_path, run_root),
                            "ordering_basis": {
                                "source_pdf_page": entry["source_pdf_page"],
                                "surface_order": entry["surface_order"],
                                "block_order_within_logical_page": block_order_within_logical_page,
                            },
                            "segmentation_basis": {
                                "rule": "consecutive-non-empty-lines-separated-by-blank-lines",
                                "line_count": len(block_text.splitlines()),
                            },
                            "lineage": {
                                "logical_page_id": logical_page_id,
                                "logical_page_order": logical_page_order,
                                "logical_page_evidence_text_path": evidence_text_path_relative,
                                "source_pdf_page": entry["source_pdf_page"],
                                "surface_id": entry["surface_id"],
                                "surface_role": entry["surface_role"],
                                "surface_order": entry["surface_order"],
                                "source_spread_png_path": entry["source_spread_png_path"],
                                "derived_png_path": entry["derived_png_path"],
                                "stage1_ocr_text_path": entry["ocr_text_path"],
                            },
                            "upstream_ocr": {
                                "ocr_text_length": entry["ocr_text_length"],
                                "ocr_confidence_mean": entry["ocr_confidence_mean"],
                                "ocr_confidence_sample_count": entry["ocr_confidence_sample_count"],
                            },
                            "uncertainty_flags": list(logical_page_record["uncertainty_flags"]),
                        }
                    )
                logical_page_record["block_order_start"] = block_order_start
                logical_page_record["block_order_end"] = len(block_units)

        logical_pages.append(logical_page_record)

    stage2_manifest_path = stage2_dir / "manifest.json"
    stage2_manifest = {
        "command": "stage2-structural-reconstruct",
        "scope": "stage-2 structural reconstruction only",
        "scope_note": _scope_note_for(reconstruction_scope),
        "status_note": (
            "Annotation interpretation and final markdown artifacts remain unimplemented in this seam."
        ),
        "non_normalization_note": _non_normalization_note_for(reconstruction_scope),
        "reconstruction_scope": reconstruction_scope,
        "generated_at_utc": _utc_now(),
        "upstream_stage1_manifest_path": _relative_path(stage1_manifest_path, run_root),
        "pdf_input": stage1_manifest.get("pdf_input"),
        "page_range": stage1_manifest.get("page_range"),
        "selected_pages": stage1_manifest.get("selected_pages"),
        "scan_layout": stage1_manifest.get("scan_layout"),
        "spread_handling": stage1_manifest.get("spread_handling"),
        "ordering_basis": ["source_pdf_page", "surface_order"],
        "ordering_confidence": {
            "value": "high",
            "note": (
                "Logical page order is taken directly from explicit Stage 1 observables: "
                "source_pdf_page ascending, then surface_order ascending."
            ),
        },
        "structure_limit_note": _structure_limit_note_for(reconstruction_scope),
        "selected_logical_page_order": selected_logical_page_order,
        "logical_pages": logical_pages,
    }
    if reconstruction_scope == "block-units":
        stage2_manifest["block_segmentation_note"] = (
            "Block units are segmented deterministically from Stage 1 OCR layout evidence as "
            "consecutive non-empty lines separated by one or more blank lines."
        )
        stage2_manifest["block_ordering_basis"] = [
            "source_pdf_page",
            "surface_order",
            "block_order_within_logical_page",
        ]
        stage2_manifest["block_ordering_confidence"] = {
            "value": "high",
            "note": (
                "Block order follows the validated logical page order, then the within-page order "
                "of blank-line-separated OCR line groups."
            ),
        }
        stage2_manifest["block_unit_count"] = len(block_units)
        stage2_manifest["block_units"] = block_units
    _write_json(stage2_manifest_path, stage2_manifest)

    result = {
        "run_root": str(run_root),
        "stage2_manifest": str(stage2_manifest_path),
        "reconstruction_scope": reconstruction_scope,
        "logical_page_count": len(logical_pages),
        "selected_logical_page_order": selected_logical_page_order,
    }
    if reconstruction_scope == "block-units":
        result["block_unit_count"] = len(block_units)
    return result


def _scope_note_for(reconstruction_scope: str) -> str:
    if reconstruction_scope == "page-units":
        return (
            "This seam reconstructs ordered logical page units from Stage 1 OCR evidence "
            "and does not claim paragraph hierarchy, chapter reconstruction, or final markdown artifacts."
        )

    return (
        "This seam reconstructs ordered logical page units and ordered block units from Stage 1 OCR "
        "layout evidence and does not perform semantic cleanup, prose rewriting, or hidden repair."
    )


def _non_normalization_note_for(reconstruction_scope: str) -> str:
    if reconstruction_scope == "page-units":
        return (
            "Stage 2 retains logical page evidence directly from Stage 1 OCR text without structural "
            "cleanup or semantic normalization."
        )

    return (
        "Stage 2 retains logical page and block evidence directly from Stage 1 OCR text without "
        "structural cleanup, prose rewriting, or semantic normalization."
    )


def _structure_limit_note_for(reconstruction_scope: str) -> str:
    if reconstruction_scope == "page-units":
        return "Paragraph, hierarchy, and chapter reconstruction are not yet modeled in this seam."

    return (
        "Cross-page paragraph continuation, hierarchy, chapter boundaries, annotation interpretation, "
        "and final markdown artifacts are not yet modeled in this seam."
    )


def _segment_ocr_text_into_blocks(ocr_text: str) -> list[str]:
    block_texts: list[str] = []
    current_lines: list[str] = []

    for line in ocr_text.splitlines():
        if line.strip():
            current_lines.append(line)
            continue

        if current_lines:
            block_texts.append("\n".join(current_lines))
            current_lines = []

    if current_lines:
        block_texts.append("\n".join(current_lines))

    return block_texts


def _validated_stage1_entries(
    stage1_manifest_path: Path,
    stage1_manifest: object,
    run_root: Path,
) -> list[dict[str, object]]:
    if not isinstance(stage1_manifest, dict):
        raise CliError(f"stage-1 manifest must contain a JSON object: {stage1_manifest_path}")
    if stage1_manifest.get("spread_handling") != "split-halves":
        raise CliError(
            "stage-1 manifest is not spread-aware split output; this Stage 2 seam expects split-halves surfaces"
        )

    raw_pages = stage1_manifest.get("pages")
    if not isinstance(raw_pages, list) or not raw_pages:
        raise CliError(f"stage-1 manifest is missing non-empty pages: {stage1_manifest_path}")

    ordering_keys: set[tuple[int, int]] = set()
    surface_orders_by_pdf_page: dict[int, set[int]] = defaultdict(set)
    validated_entries: list[dict[str, object]] = []

    for index, raw_entry in enumerate(raw_pages, start=1):
        entry_name = f"pages[{index}]"
        if not isinstance(raw_entry, dict):
            raise CliError(f"{entry_name} must be a JSON object in {stage1_manifest_path}")

        source_pdf_page = _required_int(raw_entry, "source_pdf_page", entry_name)
        surface_order = _required_int(raw_entry, "surface_order", entry_name)
        surface_id = _required_text(raw_entry, "surface_id", entry_name)
        surface_role = _required_text(raw_entry, "surface_role", entry_name)
        source_spread_png_path = _required_text(raw_entry, "source_spread_png_path", entry_name)
        derived_png_path = _required_text(raw_entry, "derived_png_path", entry_name)
        ocr_text_path = _required_text(raw_entry, "ocr_text_path", entry_name)
        ocr_text_length = _required_int(raw_entry, "ocr_text_length", entry_name)
        ocr_confidence_mean = _optional_number(raw_entry, "ocr_confidence_mean", entry_name)
        ocr_confidence_sample_count = _required_int(
            raw_entry,
            "ocr_confidence_sample_count",
            entry_name,
        )
        if ocr_confidence_sample_count < 0:
            raise CliError(f"{entry_name}.ocr_confidence_sample_count must be zero or greater")

        uncertainty_flags: list[str] = []
        if ocr_confidence_mean is None:
            uncertainty_flags.append("missing-ocr-confidence")

        ordering_key = (source_pdf_page, surface_order)
        if ordering_key in ordering_keys:
            raise CliError(
                "stage-1 manifest contains duplicate ordering keys for "
                f"source_pdf_page={source_pdf_page} and surface_order={surface_order}"
            )
        ordering_keys.add(ordering_key)

        source_spread_abs_path = _resolve_run_root_file(
            run_root=run_root,
            relative_path=source_spread_png_path,
            label="source_spread_png_path",
            entry_name=entry_name,
        )
        derived_png_abs_path = _resolve_run_root_file(
            run_root=run_root,
            relative_path=derived_png_path,
            label="derived_png_path",
            entry_name=entry_name,
        )
        ocr_text_abs_path = _resolve_run_root_file(
            run_root=run_root,
            relative_path=ocr_text_path,
            label="ocr_text_path",
            entry_name=entry_name,
        )

        surface_orders_by_pdf_page[source_pdf_page].add(surface_order)
        validated_entries.append(
            {
                "source_pdf_page": source_pdf_page,
                "surface_order": surface_order,
                "surface_id": surface_id,
                "surface_role": surface_role,
                "source_spread_png_path": source_spread_png_path,
                "derived_png_path": derived_png_path,
                "ocr_text_path": ocr_text_path,
                "ocr_text_length": ocr_text_length,
                "ocr_confidence_mean": ocr_confidence_mean,
                "ocr_confidence_sample_count": ocr_confidence_sample_count,
                "uncertainty_flags": uncertainty_flags,
                "ocr_text_abs_path": ocr_text_abs_path,
            }
        )

    if not any(len(surface_orders) > 1 for surface_orders in surface_orders_by_pdf_page.values()):
        raise CliError(
            "stage-1 manifest does not include multiple page surfaces per source PDF page; "
            "this Stage 2 seam expects spread-aware page surfaces"
        )

    for source_pdf_page, surface_orders in surface_orders_by_pdf_page.items():
        if surface_orders != {0, 1}:
            raise CliError(
                "stage-1 manifest does not provide complete left/right page-unit coverage for "
                f"source_pdf_page={source_pdf_page}; expected surface_order values {{0, 1}} but found {sorted(surface_orders)}"
            )

    return sorted(
        validated_entries,
        key=lambda entry: (entry["source_pdf_page"], entry["surface_order"]),
    )


def _read_json(path: Path) -> object:
    if not path.is_file():
        raise CliError(f"required JSON file does not exist: {path}")

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CliError(f"invalid JSON in {path}: {exc}") from exc


def _required_int(raw_entry: dict[str, object], field_name: str, entry_name: str) -> int:
    value = raw_entry.get(field_name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise CliError(f"{entry_name}.{field_name} must be an integer")
    return value


def _required_number(raw_entry: dict[str, object], field_name: str, entry_name: str) -> float | int:
    value = raw_entry.get(field_name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CliError(f"{entry_name}.{field_name} must be numeric")
    return value


def _optional_number(raw_entry: dict[str, object], field_name: str, entry_name: str) -> float | int | None:
    value = raw_entry.get(field_name)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CliError(f"{entry_name}.{field_name} must be numeric or null")
    return value


def _required_text(raw_entry: dict[str, object], field_name: str, entry_name: str) -> str:
    value = raw_entry.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise CliError(f"{entry_name}.{field_name} must be a non-empty string")
    return value


def _relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _resolve_run_root_file(
    run_root: Path,
    relative_path: str,
    label: str,
    entry_name: str,
) -> Path:
    absolute_path = (run_root / relative_path).resolve()
    run_root_resolved = run_root.resolve()

    try:
        absolute_path.relative_to(run_root_resolved)
    except ValueError as exc:
        raise CliError(
            f"{entry_name}.{label} escapes the run root and cannot be trusted for lineage: {absolute_path}"
        ) from exc

    if not absolute_path.is_file():
        raise CliError(
            f"{entry_name}.{label} does not resolve to an existing file under the run root: {absolute_path}"
        )

    return absolute_path


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")