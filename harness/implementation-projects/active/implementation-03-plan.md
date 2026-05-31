# Implementation 03 Plan

## Intent

Open a narrow successor bundle whose only purpose is to test whether a bounded Stage 1 control-surface change can improve corrected-root anchor quality without changing the current Stage 3 interpretive boundary or opening Stage 4. The proposed change is a sibling-surface extraction experiment: derive an OCR-optimized text plane and an annotation-optimized mark plane from the same rectified source surface, keep them in shared geometry, and preserve inspectable lineage from the rectified source surface to OCR anchors and mark candidates.

This bundle is not a continuation of implementation-02 family-level Stage 3 refinement. Implementation-02 is archived and already showed that further unresolved-family splitting preserved the truthful `122 total / 5 resolved / 117 unresolved` baseline without moving the readiness frontier. Implementation-03 therefore shifts upstream and uses the current Stage 3 seam as an evaluation harness rather than the primary change surface.

## Admissibility Report

- Invariant constraints: preserve the two independent markdown terminal artifacts and the four explicit stages; preserve local-only CLI posture; preserve typed provenance and visible uncertainty; preserve the distinction between direct extraction, structural inference, semantic expansion, unresolved content, and missing content; preserve the current interpretive boundary that forbids forcing ambiguous, enclosure-like, marginalia, or no-anchor cases into confident spans; keep Stage 4 closed.
- Task constraints: open implementation-03 as the sole live bundle under `active/`; scope this bundle to a corrected-root Stage 1 sibling-surface experiment only; use the current Stage 3 promotion boundary unchanged as the initial evaluation harness; do not reopen `novel_and_hilite_extraction/stage2.py`, `harness/open-decisions.md`, or the project-spec templates; do not touch Stage 4 artifact synthesis or artifact schemas.
- Constraint conflicts: the current Stage 1 path still runs OCR and annotation extraction from the same derived image surface, so OCR anchor quality and mark extraction quality are coupled on one control surface. Implementation-02 showed that repeated Stage 3 family refinement preserved the conservative baseline without changing the five clean resolutions or the unresolved frontier. If the sibling-surface experiment cannot preserve shared geometry and inspectable lineage, or if it pressures Stage 3 into a broader interpretive change rather than an upstream evidence improvement, stop instead of widening scope implicitly.
- Allowed transformation types: maintain this plan and tracker; modify `novel_and_hilite_extraction/stage1.py` and Stage 1 retained evidence surfaces to derive an OCR-optimized text plane plus an annotation-optimized mark plane from the same rectified source surface; retain shared-geometry and lineage fields needed to inspect how OCR anchors and mark candidates were derived; rerun corrected roots through the existing Stage 3 seam without changing its promotion rule; add corrected-root validation evidence and wording alignment needed to describe the experiment truthfully; open a narrow Stage 3 compatibility edit only if the new Stage 1 evidence cannot flow through the current Stage 3 inputs without it.
- Affected surfaces: `harness/implementation-projects/active/implementation-03-plan.md`; `harness/implementation-projects/active/implementation-03-tracker.md`; `novel_and_hilite_extraction/stage1.py`; corrected-root Stage 1 and Stage 3 validation probes and retained manifests under the local temp workspace.
- Non-affected surfaces: `novel_and_hilite_extraction/stage2.py`; `novel_and_hilite_extraction/stage3.py` for the initial experiment seam; Stage 4 artifact synthesis and all artifact-schema surfaces; `harness/open-decisions.md`; `harness/project-spec/template-project-spec.md`; `harness/project-spec/template-governance-primitives.md`; auth, storage, deployment, billing, or remote-provider surfaces.
- Admissibility checks:
  - pass: implementation-02 is archived and `active/` is empty, so a successor bundle can open cleanly.
  - pass: improving extraction quality and inspectability inside Stage 1 is admissible without amending the project spec.
  - pass: the current user instruction authorizes opening a new successor seam rather than continuing archived implementation-02.
  - pass: Stage 4 remains closed and no artifact-schema or interpretive-boundary change is authorized in this bundle.
  - blocked pending runtime proof: the sibling-surface experiment must show whether recoverable unresolved buckets can decrease on corrected roots while preserving the current five clean resolutions and zero resolved bracket-or-box interpretations.
- Stop conditions: stop if the experiment requires a Stage 4 opening, artifact-schema change, open-decisions amendment, or project-spec amendment; stop if it cannot preserve shared geometry and inspectable lineage between rectified source, text plane, mark plane, OCR anchors, and mark candidates; stop if it requires external-provider, storage, auth, or deployment changes; stop if it forces ambiguous, enclosure-like, marginalia, or no-anchor cases into confident interpretations; stop if a required Stage 3 edit grows beyond narrow compatibility with unchanged promotion rules.

## Planned Seams

1. Corrected-root baseline pin and measurement contract.
   Freeze the archived corrected-root baseline for comparison: `122 total / 5 resolved / 117 unresolved`, zero resolved bracket-or-box interpretations, `36 missing-anchor-and-empty-text-unresolved`, and `27 ambiguous-underline-anchor-unresolved`.

2. Stage 1 sibling-surface extraction and lineage retention.
   Derive an OCR-optimized text plane and an annotation-optimized mark plane from the same rectified source surface, keep them in shared coordinate space, and retain inspectable lineage to OCR anchors and mark candidates.

3. Corrected-root rerun through the unchanged Stage 3 evaluation harness.
   Re-run corrected roots through the modified Stage 1 path and the current Stage 3 seam without changing Stage 3 promotion rules. Compare the resulting unresolved buckets and resolved set against the archived baseline.

4. Narrow compatibility adjustment only if required.
   If the new Stage 1 evidence cannot be consumed truthfully by the current Stage 3 seam, open the smallest compatibility edit needed to preserve the current promotion boundary and rerun the same corrected-root comparison.

5. Closeout and decision checkpoint.
   Archive the bundle with either positive evidence that the sibling-surface experiment improved recoverable buckets while preserving truthfulness, or a grounded negative result that shows the experiment did not materially improve the current frontier.

## Non-Goals

- Do not open Stage 4 artifact synthesis.
- Do not define or change either terminal markdown artifact schema.
- Do not broaden the current Stage 3 interpretive boundary or promotion rule as part of the initial experiment.
- Do not repurpose this bundle into another unresolved-family taxonomy pass.
- Do not modify `novel_and_hilite_extraction/stage2.py`.
- Do not add external-provider, storage, deployment, or auth commitments.

## Acceptance Criteria

- Implementation-03 is the only live numbered bundle under `active/`.
- A corrected-root rerun preserves the current five clean resolved highlight-or-underline interpretations and preserves zero resolved bracket-or-box interpretations.
- At least one recoverable-looking unresolved bucket decreases on corrected roots without over-promotion: `missing-anchor-and-empty-text-unresolved` drops below 36, or `ambiguous-underline-anchor-unresolved` drops below 27.
- If neither bucket improves, the bundle closes with a grounded negative result that explains the failure without widening scope or opening Stage 4.
- The Stage 1 evidence retains inspectable lineage between the rectified source surface, OCR-optimized text plane, annotation-optimized mark plane, OCR anchors, and mark candidates.
- Stage 4 remains unopened and unclaimed throughout the bundle.

## Current Repo Runtime State

- Implementation-02 is archived and preserved the truthful corrected-root Stage 3 baseline at `122 total / 5 resolved / 117 unresolved` while improving unresolved-family specificity only.
- The current Stage 1 path derives OCR output and annotation observables from the same cropped derived image surface, even though the annotation branch already subtracts OCR text anchors from some dark-mark detection logic.
- The current Stage 3 path still resolves only clean highlight or underline candidates with confidence at least `0.6`, empty Stage 1 uncertainty flags, valid anchor references, and no enclosure-like relation.
- The strongest recoverable-looking unresolved populations on the archived corrected-root proof surface are `36 missing-anchor-and-empty-text-unresolved` and `27 ambiguous-underline-anchor-unresolved`.
- The corrected-root proof surfaces remain the authoritative basis for intent-level claims, and stale pre-rectification roots remain out of bounds.
- Stage 4 remains closed because the archived formatting probe proved only throwaway artifact-shape renderability and did not establish honest artifact readiness.

## Assumptions And Unknowns

- Assumption: the corrected full-packet and corrected anchor-suite roots remain the only valid proof surfaces for this successor work.
- Assumption: a sibling OCR-optimized text plane can improve OCR anchor quality without breaking shared geometry with annotation masks and mark candidates.
- Assumption: the current Stage 3 promotion boundary is strict enough to serve as an honest evaluation harness for upstream evidence improvements.
- Unknown: whether the `missing-anchor-and-empty-text-unresolved` population is primarily caused by OCR loss on the shared surface, by mark-to-anchor relation logic, or by genuinely textless annotations.
- Unknown: whether the `ambiguous-underline-anchor-unresolved` population is primarily geometric ambiguity that can be reduced upstream, or genuine multi-line ambiguity that should remain unresolved.
- Unknown: whether the Stage 1 retained evidence format can express the sibling-surface lineage truthfully without any Stage 3 compatibility edits.
- Unknown: whether a negative result from this experiment will imply the next honest move is a narrower relation-geometry seam rather than another OCR-plane refinement.

## Affected and Non-Affected Surfaces

- Affected: `harness/implementation-projects/active/implementation-03-plan.md`; `harness/implementation-projects/active/implementation-03-tracker.md`; `novel_and_hilite_extraction/stage1.py`; corrected-root Stage 1 and Stage 3 validation probes and manifests.
- Non-affected: `novel_and_hilite_extraction/stage2.py`; `novel_and_hilite_extraction/stage3.py` for the initial experiment seam; `harness/open-decisions.md`; `harness/project-spec/template-project-spec.md`; `harness/project-spec/template-governance-primitives.md`; all Stage 4 artifact-synthesis surfaces.

## Completion Rule

- Do not mark behavior complete on fixture, mock, dry-run, serialization, type, field, file, path, route, crate, config, or nominal-caller evidence alone.

## Approval Gates

- [ ] Schema
- [ ] API
- [ ] Auth
- [ ] Storage
- [ ] Deployment
- [ ] Destructive operation
- [ ] Broad architecture
- [ ] Project-intent authority not covered by spec or current authorization

## Closeout Note

- When this bundle completes, move it from `active/` to `archive/`.