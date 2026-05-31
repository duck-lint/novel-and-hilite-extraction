# Implementation 01 Summary

## Final Status

- Project prefix: implementation-01
- Final status: archived
- Goal: establish the first live local runtime through prep, Stage 1 visual extraction, Stage 2 structural reconstruction, and a bounded corrected-root Stage 3 annotation-interpretation seam while keeping the two-artifact and four-stage contract honest about what remained unimplemented.

## Files And Surfaces Changed

- `novel_and_hilite_extraction/__main__.py`
- `novel_and_hilite_extraction/stage1.py`
- `novel_and_hilite_extraction/stage2.py`
- `novel_and_hilite_extraction/stage3.py`
- `config/dirs.yaml`
- `harness/implementation-projects/active/implementation-01-plan.md` and `harness/implementation-projects/active/implementation-01-tracker.md`, now archived
- `harness/known-failures.md`
- corrected-root validation run roots under the local temp workspace used for Stage 1, Stage 2, and Stage 3 proof probes

## Verification Evidence

- Corrected Stage 1 rotated-spread validation passed on anchor and full-packet roots, including the layout-aware default rotation path and explicit no-rotation opt-out.
- Corrected Stage 2 validation passed at `page-units` and bounded `block-units` scope on the rotated-spread proof roots.
- Corrected Stage 3 validation at `C:\Users\madis\AppData\Local\Temp\novel-stage3-semantic-entry-check-7dd07e5e-5c7d-48d9-a64d-767dcba28e9f\anchor-suite-stage1` passed with 122 total interpretations, 5 resolved, and 117 unresolved.
- The corrected Stage 3 truthfulness probe kept exactly two resolved interpretations on `pdf-page-0020-right`, exactly two resolved interpretations on `pdf-page-0024-left`, no resolved enclosure-like interpretation on `pdf-page-0024-left`, and zero resolved interpretations on `pdf-page-0025-right`, `pdf-page-0028-left`, and `pdf-page-0028-right`.
- Focused diagnostics passed for the final Stage 3 payload-alignment updates and the active-bundle memory reconciliation.

## User-Facing Acceptance Result

- Pass: bounded corrected-root Stage 3 truthfulness probe. Clean highlight or underline cases resolve conservatively with anchor-local `resolved_span_text` plus widened `semantic_entry_text`, while ambiguity, enclosure-like relations, marginalia, no-anchor cases, bleed-through, and clean-surface anchors remain unresolved or non-promoted.
- Deferred by scope: Stage 4 artifact synthesis and both markdown terminal artifacts were intentionally left unopened in implementation-01.

## Decisions Made

- The first live stack uses `pypdfium2`, `Pillow`, `opencv-python`, `pytesseract`, and local Tesseract OCR.
- Rotated two-page spreads use a layout-aware default rectification path with explicit `--spread-rotation-deg 0` opt-out.
- Corrected roots, not pre-rectification roots, are authoritative for intent-level claims.
- Resolved Stage 3 entries preserve anchor-local `resolved_span_text` and expose widened `semantic_entry_text` for bounded local context.

## Known Failures Added Or Updated

- `KF-001`: active bundle summary drift after seam widening was recorded and reconciled before archive.

## Unresolved Risks And Revisit Triggers

- The bounded Stage 3 seam still resolves only 5 of 122 corrected-root interpretations; broader Stage 3 semantics are the next proof frontier.
- Stage 4 should not open on top of the current bounded local-context seam without additional corrected-root semantic proof.
- Pre-rectification roots remain stale for intent-level claims and should not be reused as proof surfaces.

## Next End Goal

- Open implementation-02 as the sole live bundle and broaden Stage 3 semantics on corrected roots before any Stage 4 artifact synthesis.