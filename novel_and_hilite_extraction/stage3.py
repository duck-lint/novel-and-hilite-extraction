from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


class CliError(RuntimeError):
    pass


_RESOLVABLE_CLASSES = {"highlight", "underline"}
_MIN_CONFIDENT_DETECTION = 0.6
_CONTEXT_LINE_RADIUS = 1


def _derive_interpretation_kind(
    normalized_class: str, unresolved_reason_codes: list[str]
) -> str:
    if not unresolved_reason_codes:
        return f"{normalized_class}-local-context"

    reason_codes = set(unresolved_reason_codes)
    if "marginalia-not-resolved-in-this-seam" in reason_codes:
        return "marginalia-unresolved"
    if (
        "enclosure-mark-not-resolved-in-this-seam" in reason_codes
        or "enclosure-like-relation-not-resolved-in-this-seam" in reason_codes
    ):
        if "unknown-mark-form" in reason_codes:
            return "enclosure-like-unknown-mark-unresolved"
        if normalized_class == "underline":
            return "enclosure-like-underline-unresolved"
        if normalized_class == "highlight":
            return "enclosure-like-highlight-unresolved"
        return "enclosure-like-unresolved"
    if "ambiguous-anchor-evidence" in reason_codes:
        if "unknown-mark-form" in reason_codes:
            return "ambiguous-anchor-unknown-mark-unresolved"
        if normalized_class == "underline":
            return "ambiguous-underline-anchor-unresolved"
        if normalized_class == "highlight":
            return "ambiguous-highlight-anchor-unresolved"
        return "ambiguous-anchor-unresolved"
    if "unresolved-anchor-reference" in reason_codes:
        return "unresolved-anchor-reference-unresolved"
    if "missing-anchor-evidence" in reason_codes and "empty-anchor-text" in reason_codes:
        return "missing-anchor-and-empty-text-unresolved"
    if "missing-anchor-evidence" in reason_codes:
        return "missing-anchor-evidence-unresolved"
    if "empty-anchor-text" in reason_codes:
        return "empty-anchor-text-unresolved"
    if (
        "below-stage1-confidence-threshold" in reason_codes
        or "missing-stage1-detection-confidence" in reason_codes
    ):
        return "low-confidence-unresolved"
    if "unknown-mark-form" in reason_codes:
        return "unknown-mark-unresolved"
    if "normalized-class-not-resolved-in-this-seam" in reason_codes:
        return "normalized-class-unresolved"
    if "stage1-uncertainty-present" in reason_codes:
        return "stage1-uncertainty-unresolved"
    return "unresolved"


def run_stage3_annotation_interpret(run_root: Path) -> dict[str, object]:
    if not run_root.is_dir():
        raise CliError(f"run root does not exist: {run_root}")

    stage1_manifest_path = run_root / "stage-1-visual-extraction" / "manifest.json"
    stage1_manifest = _read_json(stage1_manifest_path)
    ordered_entries = _validated_stage1_entries(
        stage1_manifest_path=stage1_manifest_path,
        stage1_manifest=stage1_manifest,
        run_root=run_root,
    )

    stage3_dir = run_root / "stage-3-annotation-interpretation"
    if stage3_dir.exists():
        raise CliError(f"stage-3 annotation interpretation evidence already exists: {stage3_dir}")
    stage3_dir.mkdir(parents=True, exist_ok=False)

    selected_interpretation_order: list[dict[str, object]] = []
    interpretations: list[dict[str, object]] = []
    surface_summaries: list[dict[str, object]] = []

    interpretation_order = 0
    resolved_interpretation_count = 0
    unresolved_interpretation_count = 0

    for entry in ordered_entries:
        anchor_payload = _read_json(entry["ocr_anchor_abs_path"])
        candidate_payload = _read_json(entry["annotation_mark_candidates_abs_path"])
        word_index, line_index = _build_anchor_indexes(anchor_payload)
        ordered_surface_line_ids = _ordered_line_ids(line_index)
        relations_by_candidate = _group_anchor_relations(candidate_payload)
        mark_candidates = candidate_payload.get("mark_candidates")
        if not isinstance(mark_candidates, list):
            raise CliError(
                "stage-1 annotation candidate payload must contain a mark_candidates list: "
                f"{entry['annotation_mark_candidates_abs_path']}"
            )

        surface_summary = {
            "surface_id": entry["surface_id"],
            "source_pdf_page": entry["source_pdf_page"],
            "surface_role": entry["surface_role"],
            "surface_order": entry["surface_order"],
            "candidate_count": len(mark_candidates),
            "resolved_interpretation_count": 0,
            "unresolved_interpretation_count": 0,
            "ambiguity_bearing_candidate_count": 0,
        }

        for candidate_order_within_surface, raw_candidate in enumerate(mark_candidates, start=1):
            if not isinstance(raw_candidate, dict):
                raise CliError(
                    "stage-1 mark_candidates entries must be objects: "
                    f"{entry['annotation_mark_candidates_abs_path']}"
                )

            candidate_id = _required_string(raw_candidate, "candidate_id")
            interpretation_order += 1
            interpretation_id = f"annotation-interpretation-{interpretation_order:04d}"
            candidate_relations = relations_by_candidate[candidate_id]

            interpretation = _build_interpretation_record(
                interpretation_id=interpretation_id,
                candidate_order_within_surface=candidate_order_within_surface,
                candidate=raw_candidate,
                candidate_relations=candidate_relations,
                entry=entry,
                run_root=run_root,
                stage1_manifest_path=stage1_manifest_path,
                word_index=word_index,
                line_index=line_index,
                ordered_line_ids=ordered_surface_line_ids,
            )

            if interpretation["interpretation_status"] == "resolved":
                evidence_text_path = stage3_dir / f"{interpretation_id}.txt"
                evidence_text = str(interpretation["text_evidence"]["semantic_entry_text"])
                evidence_text_path.write_text(evidence_text + "\n", encoding="utf-8")
                interpretation["text_evidence"]["evidence_text_path"] = _relative_path(
                    evidence_text_path,
                    run_root,
                )
                resolved_interpretation_count += 1
                surface_summary["resolved_interpretation_count"] += 1
            else:
                unresolved_interpretation_count += 1
                surface_summary["unresolved_interpretation_count"] += 1

            if "ambiguous-anchor" in interpretation["uncertainty_flags"]:
                surface_summary["ambiguity_bearing_candidate_count"] += 1

            interpretations.append(interpretation)
            selected_interpretation_order.append(
                {
                    "interpretation_id": interpretation_id,
                    "interpretation_status": interpretation["interpretation_status"],
                    "source_pdf_page": entry["source_pdf_page"],
                    "surface_order": entry["surface_order"],
                    "surface_id": entry["surface_id"],
                    "candidate_id": candidate_id,
                }
            )

        surface_summaries.append(surface_summary)

    stage3_manifest_path = stage3_dir / "manifest.json"
    stage3_manifest = {
        "command": "stage3-annotation-interpret",
        "scope": "stage-3 annotation interpretation only",
        "scope_note": (
            "This seam resolves only bounded local-context highlight or underline interpretations "
            "with explicit Stage 1 OCR-anchor support. It does not synthesize markdown artifacts, "
            "infer themes or author intent, or force ambiguous, enclosure-like, no-anchor, or "
            "marginalia cases into confident text spans."
        ),
        "status_note": (
            "Stage 4 artifact synthesis and the final markdown outputs remain unimplemented in this seam."
        ),
        "claim_boundary_note": (
            "Resolved interpretations are limited to Stage 1 candidates whose normalized class is "
            "highlight or underline, whose Stage 1 detection confidence is at least 0.6, whose "
            "uncertainty flags are empty, whose linked OCR anchors resolve against retained Stage 1 "
            "anchor tables, and whose candidate relations are not enclosure-like. Resolved entries may "
            "expand to one neighboring OCR line before and after the marked line set on the same surface. "
            "Every other candidate is carried forward as unresolved with explicit reasons."
        ),
        "non_normalization_note": (
            "Resolved text evidence is retained directly from linked Stage 1 OCR word anchors with an "
            "explicit line-anchor fallback, then widened only by a one-line local context window on the "
            "same surface. This seam does not rewrite OCR text or merge separate annotation candidates "
            "into artifact-level claims."
        ),
        "generated_at_utc": _utc_now(),
        "upstream_stage1_manifest_path": _relative_path(stage1_manifest_path, run_root),
        "pdf_input": stage1_manifest.get("pdf_input"),
        "page_range": stage1_manifest.get("page_range"),
        "selected_pages": stage1_manifest.get("selected_pages"),
        "scan_layout": stage1_manifest.get("scan_layout"),
        "spread_handling": stage1_manifest.get("spread_handling"),
        "run_root_scope": ".",
        "interpretation_selection_rule": {
            "resolvable_classes": sorted(_RESOLVABLE_CLASSES),
            "minimum_stage1_detection_confidence": _MIN_CONFIDENT_DETECTION,
            "requires_empty_stage1_uncertainty_flags": True,
            "requires_linked_ocr_anchor_ids": True,
            "forbids_enclosure_like_relations": True,
            "context_line_radius": _CONTEXT_LINE_RADIUS,
        },
        "resolved_interpretation_count": resolved_interpretation_count,
        "unresolved_interpretation_count": unresolved_interpretation_count,
        "selected_interpretation_order": selected_interpretation_order,
        "surface_summaries": surface_summaries,
        "interpretations": interpretations,
    }
    _write_json(stage3_manifest_path, stage3_manifest)

    return {
        "run_root": str(run_root),
        "stage3_manifest": str(stage3_manifest_path),
        "resolved_interpretation_count": resolved_interpretation_count,
        "unresolved_interpretation_count": unresolved_interpretation_count,
        "interpretation_count": len(interpretations),
    }


def _build_interpretation_record(
    interpretation_id: str,
    candidate_order_within_surface: int,
    candidate: dict[str, object],
    candidate_relations: list[dict[str, object]],
    entry: dict[str, object],
    run_root: Path,
    stage1_manifest_path: Path,
    word_index: dict[str, dict[str, object]],
    line_index: dict[str, dict[str, object]],
    ordered_line_ids: list[str],
) -> dict[str, object]:
    candidate_id = _required_string(candidate, "candidate_id")
    normalized_class = str(candidate.get("normalized_class") or "unknown")
    stage1_detection_confidence = _coerce_float(candidate.get("detection_confidence"))
    uncertainty_flags = _sorted_unique_strings(candidate.get("uncertainty_flags", []))
    linked_ocr_word_ids = _ordered_unique_strings(candidate.get("linked_ocr_word_ids", []))
    linked_ocr_line_ids = _ordered_unique_strings(candidate.get("linked_ocr_line_ids", []))
    relation_types = _sorted_unique_strings(
        [
            *candidate.get("relation_types", []),
            *(relation.get("relation_type") for relation in candidate_relations),
        ]
    )
    missing_linked_word_ids = [word_id for word_id in linked_ocr_word_ids if word_id not in word_index]
    missing_linked_line_ids = [line_id for line_id in linked_ocr_line_ids if line_id not in line_index]
    anchor_text_evidence = _resolve_anchor_text_evidence(
        linked_ocr_word_ids=linked_ocr_word_ids,
        linked_ocr_line_ids=linked_ocr_line_ids,
        word_index=word_index,
        line_index=line_index,
        ordered_line_ids=ordered_line_ids,
    )

    unresolved_reason_codes: list[str] = []
    if normalized_class not in _RESOLVABLE_CLASSES:
        if normalized_class == "marginalia":
            unresolved_reason_codes.append("marginalia-not-resolved-in-this-seam")
        elif normalized_class == "bracket-or-box":
            unresolved_reason_codes.append("enclosure-mark-not-resolved-in-this-seam")
        elif normalized_class == "unknown":
            unresolved_reason_codes.append("unknown-mark-form")
        else:
            unresolved_reason_codes.append("normalized-class-not-resolved-in-this-seam")
    if stage1_detection_confidence is None:
        unresolved_reason_codes.append("missing-stage1-detection-confidence")
    elif stage1_detection_confidence < _MIN_CONFIDENT_DETECTION:
        unresolved_reason_codes.append("below-stage1-confidence-threshold")
    if uncertainty_flags:
        unresolved_reason_codes.append("stage1-uncertainty-present")
    if "ambiguous-anchor" in uncertainty_flags or any(
        bool(relation.get("ambiguous")) for relation in candidate_relations
    ):
        unresolved_reason_codes.append("ambiguous-anchor-evidence")
    if "encloses-text-region" in relation_types:
        unresolved_reason_codes.append("enclosure-like-relation-not-resolved-in-this-seam")
    if not linked_ocr_word_ids and not linked_ocr_line_ids:
        unresolved_reason_codes.append("missing-anchor-evidence")
    if missing_linked_word_ids or missing_linked_line_ids:
        unresolved_reason_codes.append("unresolved-anchor-reference")
    if not str(anchor_text_evidence["anchor_text"]).strip():
        unresolved_reason_codes.append("empty-anchor-text")

    unresolved_reason_codes = _ordered_unique_strings(unresolved_reason_codes)
    interpretation_status = "resolved" if not unresolved_reason_codes else "unresolved"
    interpretation_kind = _derive_interpretation_kind(
        normalized_class=normalized_class,
        unresolved_reason_codes=unresolved_reason_codes,
    )

    return {
        "interpretation_id": interpretation_id,
        "interpretation_status": interpretation_status,
        "interpretation_kind": interpretation_kind,
        "candidate_id": candidate_id,
        "candidate_order_within_surface": candidate_order_within_surface,
        "normalized_class": normalized_class,
        "bbox_px": candidate.get("bbox_px"),
        "pixel_area": candidate.get("pixel_area"),
        "contour_area": candidate.get("contour_area"),
        "source_pdf_page": entry["source_pdf_page"],
        "surface_id": entry["surface_id"],
        "surface_role": entry["surface_role"],
        "surface_order": entry["surface_order"],
        "uncertainty_flags": uncertainty_flags,
        "confidence": {
            "stage1_detection_confidence": stage1_detection_confidence,
            "interpretation_confidence": (
                stage1_detection_confidence if interpretation_status == "resolved" else None
            ),
            "interpretation_confidence_basis": (
                "Promote Stage 1 candidate confidence only for clean highlight or underline candidates "
                "with retained anchor evidence."
            ),
        },
        "interpretation_basis": {
            "selection_rule": (
                "Resolve only clean Stage 1 highlight or underline candidates with confidence at least "
                "0.6, no Stage 1 uncertainty flags, anchor references that resolve against retained OCR "
                "anchor tables, and no enclosure-like relation. Then widen the resolved span by at most "
                "one neighboring OCR line before and after the marked line set on the same surface."
            ),
            "text_resolution_mode": anchor_text_evidence["source_mode"],
            "context_expansion_mode": anchor_text_evidence["context_mode"],
            "context_line_radius": _CONTEXT_LINE_RADIUS,
            "marked_line_count": len(anchor_text_evidence["marked_line_ids"]),
            "context_line_count": len(anchor_text_evidence["context_line_ids"]),
            "relation_types": relation_types,
            "candidate_relation_count": len(candidate_relations),
        },
        "text_evidence": {
            "source_mode": anchor_text_evidence["source_mode"],
            "anchor_text": anchor_text_evidence["anchor_text"],
            "line_texts": anchor_text_evidence["line_texts"],
            "resolved_span_text": anchor_text_evidence["anchor_text"],
            "semantic_entry_text": (
                anchor_text_evidence["context_text"] or anchor_text_evidence["anchor_text"]
            ),
            "marked_line_ids": anchor_text_evidence["marked_line_ids"],
            "context_line_ids": anchor_text_evidence["context_line_ids"],
            "context_before_lines": anchor_text_evidence["context_before_lines"],
            "context_after_lines": anchor_text_evidence["context_after_lines"],
            "context_before_text": "\n".join(anchor_text_evidence["context_before_lines"]),
            "context_after_text": "\n".join(anchor_text_evidence["context_after_lines"]),
            "context_text": anchor_text_evidence["context_text"],
            "evidence_text_path": None,
        },
        "anchor_evidence": {
            "linked_ocr_word_ids": linked_ocr_word_ids,
            "linked_ocr_line_ids": linked_ocr_line_ids,
            "missing_linked_ocr_word_ids": missing_linked_word_ids,
            "missing_linked_ocr_line_ids": missing_linked_line_ids,
            "anchor_relations": candidate_relations,
        },
        "unresolved_reason_codes": unresolved_reason_codes,
        "lineage": {
            "run_root_scope": ".",
            "source_pdf_page": entry["source_pdf_page"],
            "surface_id": entry["surface_id"],
            "surface_role": entry["surface_role"],
            "surface_order": entry["surface_order"],
            "stage1_manifest_path": _relative_path(stage1_manifest_path, run_root),
            "stage1_ocr_anchor_json_path": entry["ocr_anchor_json_path"],
            "stage1_annotation_mark_candidates_path": entry[
                "annotation_mark_candidates_path"
            ],
            "stage1_ocr_text_path": entry["ocr_text_path"],
            "stage1_derived_png_path": entry["derived_png_path"],
        },
    }


def _resolve_anchor_text_evidence(
    linked_ocr_word_ids: list[str],
    linked_ocr_line_ids: list[str],
    word_index: dict[str, dict[str, object]],
    line_index: dict[str, dict[str, object]],
    ordered_line_ids: list[str],
) -> dict[str, object]:
    ordered_words = [word_index[word_id] for word_id in linked_ocr_word_ids if word_id in word_index]
    ordered_words.sort(key=lambda item: int(item.get("reading_order") or 0))

    if ordered_words:
        grouped_line_words: defaultdict[str, list[str]] = defaultdict(list)
        line_order: dict[str, int] = {}
        for word_anchor in ordered_words:
            line_id = str(word_anchor.get("ocr_line_id") or "")
            text = str(word_anchor.get("text") or "").strip()
            if text:
                grouped_line_words[line_id].append(text)
            line_anchor = line_index.get(line_id)
            if line_anchor is not None:
                line_order[line_id] = int(line_anchor.get("reading_order") or 0)
            else:
                line_order.setdefault(line_id, int(word_anchor.get("reading_order") or 0))

        marked_line_ids = sorted(grouped_line_words, key=lambda line_id: line_order.get(line_id, 0))
        line_texts = [" ".join(grouped_line_words[line_id]) for line_id in marked_line_ids]
        return _build_contextual_text_evidence(
            source_mode="word-anchors",
            anchor_text="\n".join(line_texts),
            line_texts=line_texts,
            marked_line_ids=marked_line_ids,
            line_index=line_index,
            ordered_line_ids=ordered_line_ids,
        )

    ordered_lines = [line_index[line_id] for line_id in linked_ocr_line_ids if line_id in line_index]
    ordered_lines.sort(key=lambda item: int(item.get("reading_order") or 0))
    line_texts = [str(line_anchor.get("text") or "").strip() for line_anchor in ordered_lines]
    line_texts = [line_text for line_text in line_texts if line_text]
    marked_line_ids = [
        str(line_anchor.get("ocr_line_id") or "")
        for line_anchor in ordered_lines
        if str(line_anchor.get("ocr_line_id") or "")
    ]
    if line_texts:
        return _build_contextual_text_evidence(
            source_mode="line-anchors",
            anchor_text="\n".join(line_texts),
            line_texts=line_texts,
            marked_line_ids=marked_line_ids,
            line_index=line_index,
            ordered_line_ids=ordered_line_ids,
        )

    return {
        "source_mode": "none",
        "context_mode": "none",
        "anchor_text": "",
        "line_texts": [],
        "marked_line_ids": [],
        "context_line_ids": [],
        "context_before_lines": [],
        "context_after_lines": [],
        "context_text": "",
    }


def _build_contextual_text_evidence(
    source_mode: str,
    anchor_text: str,
    line_texts: list[str],
    marked_line_ids: list[str],
    line_index: dict[str, dict[str, object]],
    ordered_line_ids: list[str],
) -> dict[str, object]:
    context_line_ids = _expanded_context_line_ids(marked_line_ids, ordered_line_ids)
    marked_line_id_set = set(marked_line_ids)
    marked_indexes = [
        index for index, line_id in enumerate(context_line_ids) if line_id in marked_line_id_set
    ]
    first_marked_index = min(marked_indexes) if marked_indexes else 0
    last_marked_index = max(marked_indexes) if marked_indexes else -1
    context_before_lines: list[str] = []
    context_after_lines: list[str] = []
    context_line_texts: list[str] = []

    for index, line_id in enumerate(context_line_ids):
        line_text = str(line_index.get(line_id, {}).get("text") or "").strip()
        if not line_text:
            continue
        context_line_texts.append(line_text)
        if index < first_marked_index:
            context_before_lines.append(line_text)
        elif index > last_marked_index:
            context_after_lines.append(line_text)

    return {
        "source_mode": source_mode,
        "context_mode": (
            "line-neighborhood" if context_line_ids != marked_line_ids else "anchor-lines-only"
        ),
        "anchor_text": anchor_text,
        "line_texts": line_texts,
        "marked_line_ids": marked_line_ids,
        "context_line_ids": context_line_ids,
        "context_before_lines": context_before_lines,
        "context_after_lines": context_after_lines,
        "context_text": "\n".join(context_line_texts),
    }


def _expanded_context_line_ids(marked_line_ids: list[str], ordered_line_ids: list[str]) -> list[str]:
    if not marked_line_ids:
        return []

    ordered_index = {line_id: index for index, line_id in enumerate(ordered_line_ids)}
    marked_indexes = [ordered_index[line_id] for line_id in marked_line_ids if line_id in ordered_index]
    if not marked_indexes:
        return marked_line_ids

    start_index = max(0, min(marked_indexes) - _CONTEXT_LINE_RADIUS)
    end_index = min(len(ordered_line_ids) - 1, max(marked_indexes) + _CONTEXT_LINE_RADIUS)
    return ordered_line_ids[start_index : end_index + 1]


def _ordered_line_ids(line_index: dict[str, dict[str, object]]) -> list[str]:
    ordered_lines = sorted(
        line_index.values(),
        key=lambda item: int(item.get("reading_order") or 0),
    )
    return [
        str(line_anchor.get("ocr_line_id") or "")
        for line_anchor in ordered_lines
        if str(line_anchor.get("ocr_line_id") or "")
    ]


def _build_anchor_indexes(
    anchor_payload: dict[str, object],
) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    word_anchors = anchor_payload.get("word_anchors")
    line_anchors = anchor_payload.get("line_anchors")
    if not isinstance(word_anchors, list) or not isinstance(line_anchors, list):
        raise CliError("stage-1 OCR anchor payload must contain word_anchors and line_anchors lists")

    word_index: dict[str, dict[str, object]] = {}
    for raw_word_anchor in word_anchors:
        if not isinstance(raw_word_anchor, dict):
            raise CliError("stage-1 word anchor entries must be objects")
        word_index[_required_string(raw_word_anchor, "ocr_word_id")] = raw_word_anchor

    line_index: dict[str, dict[str, object]] = {}
    for raw_line_anchor in line_anchors:
        if not isinstance(raw_line_anchor, dict):
            raise CliError("stage-1 line anchor entries must be objects")
        line_index[_required_string(raw_line_anchor, "ocr_line_id")] = raw_line_anchor

    return word_index, line_index


def _group_anchor_relations(
    candidate_payload: dict[str, object],
) -> defaultdict[str, list[dict[str, object]]]:
    relations_by_candidate: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    raw_relations = candidate_payload.get("anchor_relations", [])
    if not isinstance(raw_relations, list):
        raise CliError("stage-1 annotation candidate payload anchor_relations must be a list")

    for raw_relation in raw_relations:
        if not isinstance(raw_relation, dict):
            raise CliError("stage-1 anchor relation entries must be objects")
        candidate_id = _required_string(raw_relation, "candidate_id")
        relations_by_candidate[candidate_id].append(raw_relation)

    return relations_by_candidate


def _validated_stage1_entries(
    stage1_manifest_path: Path,
    stage1_manifest: dict[str, object],
    run_root: Path,
) -> list[dict[str, object]]:
    if stage1_manifest.get("command") != "stage1-visual-extract":
        raise CliError(
            f"unsupported stage-1 manifest command at {stage1_manifest_path}: "
            f"{stage1_manifest.get('command')!r}"
        )

    raw_pages = stage1_manifest.get("pages")
    if not isinstance(raw_pages, list) or not raw_pages:
        raise CliError(f"stage-1 manifest at {stage1_manifest_path} does not contain any pages")

    validated_entries: list[dict[str, object]] = []
    ordered_raw_pages = sorted(
        raw_pages,
        key=lambda item: (
            int(item.get("source_pdf_page") or 0),
            int(item.get("surface_order") or 0),
        ),
    )

    for raw_entry in ordered_raw_pages:
        if not isinstance(raw_entry, dict):
            raise CliError("stage-1 manifest pages entries must be objects")

        ocr_anchor_json_path = _required_string(raw_entry, "ocr_anchor_json_path")
        annotation_mark_candidates_path = _required_string(
            raw_entry,
            "annotation_mark_candidates_path",
        )
        derived_png_path = _required_string(raw_entry, "derived_png_path")
        ocr_text_path = _required_string(raw_entry, "ocr_text_path")
        ocr_anchor_abs_path = run_root / ocr_anchor_json_path
        annotation_mark_candidates_abs_path = run_root / annotation_mark_candidates_path
        derived_png_abs_path = run_root / derived_png_path
        ocr_text_abs_path = run_root / ocr_text_path
        if not ocr_anchor_abs_path.is_file():
            raise CliError(f"missing stage-1 OCR anchor payload: {ocr_anchor_abs_path}")
        if not annotation_mark_candidates_abs_path.is_file():
            raise CliError(
                f"missing stage-1 annotation candidate payload: {annotation_mark_candidates_abs_path}"
            )
        if not derived_png_abs_path.is_file():
            raise CliError(f"missing stage-1 derived surface image: {derived_png_abs_path}")
        if not ocr_text_abs_path.is_file():
            raise CliError(f"missing stage-1 OCR text evidence: {ocr_text_abs_path}")

        validated_entries.append(
            {
                "surface_id": _required_string(raw_entry, "surface_id"),
                "source_pdf_page": _required_int(raw_entry, "source_pdf_page"),
                "surface_role": _required_string(raw_entry, "surface_role"),
                "surface_order": _required_int(raw_entry, "surface_order"),
                "derived_png_path": derived_png_path,
                "ocr_text_path": ocr_text_path,
                "ocr_anchor_json_path": ocr_anchor_json_path,
                "annotation_mark_candidates_path": annotation_mark_candidates_path,
                "ocr_anchor_abs_path": ocr_anchor_abs_path,
                "annotation_mark_candidates_abs_path": annotation_mark_candidates_abs_path,
            }
        )

    return validated_entries


def _read_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise CliError(f"expected JSON file does not exist: {path}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CliError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise CliError(f"expected JSON object at {path}")
    return payload


def _write_json(destination: Path, payload: dict[str, object]) -> None:
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _required_string(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise CliError(f"expected non-empty string field {key!r}")
    return value


def _required_int(payload: dict[str, object], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise CliError(f"expected integer field {key!r}")
    return value


def _coerce_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _ordered_unique_strings(values: object) -> list[str]:
    if not isinstance(values, list):
        return []

    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value or value in seen:
            continue
        ordered.append(value)
        seen.add(value)
    return ordered


def _sorted_unique_strings(values: object) -> list[str]:
    if not isinstance(values, list):
        values = list(values)
    normalized = {value for value in values if isinstance(value, str) and value}
    return sorted(normalized)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()