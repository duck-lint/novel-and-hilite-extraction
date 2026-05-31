# Implementation 03 Tracker

## Status

- State: active
- Current seam: Seam 1, corrected-root baseline pin and measurement contract for the Stage 1 sibling-surface experiment
- Next action: implement a corrected-root Stage 1 OCR-text-plane plus mark-plane experiment, then rerun the current Stage 3 seam unchanged against the archived implementation-02 baseline

## Work Log

| Date | Agent Role | Change | Evidence | Next |
| --- | --- | --- | --- | --- |
| 2026-05-31 | Planner | Opened implementation-03 as the successor bundle for a bounded Stage 1 sibling-surface experiment after implementation-02 was archived. | `harness/implementation-projects/active/` was empty; `harness/implementation-projects/archive/implementation-02-summary.md` and `harness/implementation-projects/archive/implementation-02-tracker.md` preserve the corrected-root baseline at `122 total / 5 resolved / 117 unresolved` with `36 missing-anchor-and-empty-text-unresolved` and `27 ambiguous-underline-anchor-unresolved`; `novel_and_hilite_extraction/stage1.py` still derives OCR output and annotation observables from the same derived image surface. | Execute Seam 1 and then implement the bounded Stage 1 sibling-surface experiment. |

## Seam Status

| Seam | Owner Agent | Status | Verification | Notes |
| --- | --- | --- | --- | --- |
| Seam 1: corrected-root baseline pin and measurement contract | Planner | active | Archived implementation-02 evidence fixes the current comparison baseline at `122 total / 5 resolved / 117 unresolved`, zero resolved bracket-or-box, `36 missing-anchor-and-empty-text-unresolved`, and `27 ambiguous-underline-anchor-unresolved`. | Do not use stale pre-rectification roots. |
| Seam 2: Stage 1 sibling-surface extraction and lineage retention | Implementer | proposed | The experiment must derive an OCR-optimized text plane and an annotation-optimized mark plane from the same rectified source surface while preserving shared geometry and inspectable lineage to OCR anchors and mark candidates. | Do not change the Stage 3 promotion rule in this seam. |
| Seam 3: corrected-root rerun through the unchanged Stage 3 evaluation harness | Reviewer | proposed | A fresh corrected-root rerun must compare the same baseline buckets and resolved set while preserving the five clean resolutions and zero resolved bracket-or-box interpretations. | Stage 4 remains closed. |
| Seam 4: narrow compatibility adjustment only if needed | Implementer | proposed | Open only if the new Stage 1 evidence cannot be consumed truthfully by the current Stage 3 inputs without a minimal compatibility change that keeps the current promotion boundary intact. | Stop and re-authorize if this grows beyond compatibility. |
| Seam 5: closeout and decision checkpoint | Planner | proposed | Archive with positive evidence if recoverable buckets improve without over-promotion, or archive with a grounded negative result if the experiment does not materially improve the frontier. | Do not open Stage 4 from this bundle. |

## Blockers

| Blocker | Boundary | Owner Agent | Resolution |
| --- | --- | --- | --- |
| None at successor opening. | None | Planner | Begin with the corrected-root baseline pin and stop immediately if the Stage 1 experiment pressures artifact schemas, Stage 4, or a broader interpretive-boundary change. |

## Closeout Note

- When this bundle completes, move it from `active/` to `archive/`.