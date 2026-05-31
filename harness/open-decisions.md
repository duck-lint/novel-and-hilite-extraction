# Open Decisions

This file is the current decision authority for decisions that still matter outside an archived implementation bundle.

Do not use this file as a roadmap. Record only decisions already made, decisions required to continue the current implementation, and explicit user-provided next end goals.

## Current Decisions

| ID | Decision | Source | Status | Owner | Revisit Trigger |
| --- | --- | --- | --- | --- | --- |
| CD-001 | The system emits two independent markdown artifacts as terminal outputs: Highlight Semantics Artifact and Canonical Reconstruction Artifact. | `harness/project-spec/template-project-spec.md` | Fixed | Project authority | Only if the project spec is explicitly amended. |
| CD-002 | The runtime model is explicitly staged as visual extraction, structural reconstruction, annotation interpretation, and artifact synthesis, each with separate truth claims and failure modes. | `harness/project-spec/template-project-spec.md` | Fixed | Project authority | Only if the project spec or governance primitives are explicitly amended. |
| CD-003 | Semantic plausibility must not overwrite uncertain source reconstruction without provenance annotation, and canonical reconstruction must not semantically normalize by default. | `harness/project-spec/template-project-spec.md`; `harness/project-spec/template-governance-primitives.md` | Fixed | Project authority | Only if the project spec or governance primitives are explicitly amended. |
| CD-004 | Provenance typing and visible uncertainty are mandatory; outputs must distinguish direct extraction, structural inference, semantic expansion, and unresolved or missing content. | `harness/project-spec/template-project-spec.md`; `harness/project-spec/template-governance-primitives.md` | Fixed | Project authority | Only if the project spec or governance primitives are explicitly amended. |
| CD-005 | v1 targets scanned annotated pages first rather than born-digital or mixed-source input. | User decision on 2026-05-30 | Decided | Project authority | Revisit only if the first vertical slice cannot honestly exercise the required UX on scanned inputs. |
| CD-006 | OCR and vision execution for early development is local-only by default. | User decision on 2026-05-30 | Decided | Project authority | Revisit only if local-only processing proves insufficient and a privacy/provider decision is explicitly reopened. |
| CD-007 | The first runtime interface is a CLI batch pipeline. | User decision on 2026-05-30 | Decided | Project authority | Revisit only after the CLI proof path exists and an additional interface is justified. |
| CD-008 | Artifact provenance and confidence are encoded inline per entry or section inside each markdown artifact, without making sidecar evidence required for the artifact to stand on its own. | User decision on 2026-05-30 | Decided | Project authority | Revisit only if artifact readability or auditability fails under real sample runs. |
| CD-009 | Confidence in v1 is represented as hybrid numeric plus categorical values, preserving both machine precision and human legibility. | User decision on 2026-05-30 | Decided | Project authority | Revisit only if the chosen encoding proves confusing or redundant in real operator review. |
| CD-010 | Early development retains full stage evidence on every run. | User decision on 2026-05-30 | Decided | Project authority | Revisit only after the first honest vertical slice is stable enough to justify reduced retention. |
| CD-011 | The initial annotation taxonomy preserves the raw visible mark and also assigns a normalized class. | User decision on 2026-05-30 | Decided | Project authority | Revisit only if the taxonomy cannot faithfully represent observed marks or creates avoidable ambiguity. |
| CD-012 | Canonical reconstruction for v1 proves chapter-contiguous reconstruction rather than only page-local output or whole-book continuity. | User decision on 2026-05-30 | Decided | Project authority | Revisit only if sample availability or runtime complexity forces a smaller proving slice. |
| CD-013 | Early probes use a private local sample under project control. | User decision on 2026-05-30 | Decided | Project authority | Revisit only if a safe public regression corpus becomes necessary for collaboration or repeatable verification. |
| CD-014 | The early runtime ingress format is PDF. Rasterized page images may be derived locally as an internal working surface before downstream extraction, but PDF remains the source entry surface. | User decision on 2026-05-30 | Decided | Project authority | Revisit only if early runtime proof requires a different ingress surface or the project scope expands beyond PDF-first intake. |
| CD-015 | The first local stack to evaluate for implementation-01 uses `pypdfium2` for PDF rasterization, `Pillow` and `opencv-python` for image handling, and `pytesseract` with local Tesseract OCR for text extraction. | User approval on 2026-05-30; implementation validation on 2026-05-30 | Decided | Project authority | Revisit if the stack cannot support spread-aware prep, inspectable evidence retention, or object-class generalization without book-specific heuristics. |

## Pending Decisions

| ID | Question | Boundary | Needed For | Owner | Status |
| --- | --- | --- | --- | --- | --- |
No pending decisions recorded.

## Notes

- Link to archived implementation summaries or decision files when a decision's evidence lives there.
- Do not point active decisions at stale files under `active/` after a bundle has moved to `archive/`.
- Remove decisions that no longer affect current or paused implementation work, or move their final context into the archived bundle summary.
