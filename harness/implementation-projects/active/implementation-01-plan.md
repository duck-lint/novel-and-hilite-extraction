# Implementation 01 Plan

## Intent

Open the first active implementation bundle for a planning-only proving slice, without choosing tooling or building runtime yet.

Delivery posture: define the first honest runtime contract as local-only, CLI batch, scanned annotated pages first, chapter-contiguous reconstruction first, with PDF as ingress and an explicit PDF-to-PNG page conversion step before downstream processing.

The current source shape is a scanned PDF rendered as two-page spreads from a facedown photocopier workflow. Implementation-01 records that shape as an input constraint for the proof contract without yet choosing a split, crop, or rectification strategy.

Observed evidence: there is no runtime yet, the active bundle slot is empty, and the configured roots already distinguish PDF source, PNG working files, and markdown outputs.

Sample identity and exact qualification remain deferred as a required seam before runtime proof, not as a blocker to opening implementation-01.

## Admissibility Report

- Invariant constraints: preserve two independent markdown terminal artifacts; preserve the four explicit stages of visual extraction, structural reconstruction, annotation interpretation, and artifact synthesis; preserve canonical non-normalization by default; preserve typed provenance and visible uncertainty; preserve local-only first proof, scanned annotated pages first, CLI batch first, and chapter-contiguous reconstruction first.
- Task constraints: open implementation-01 now; keep sample qualification deferred but required before runtime proof; treat PDF as the input format; make PDF-to-PNG conversion explicit in the first runtime slice; do not implement runtime in this bundle-opening step.
- Constraint conflicts: none at bundle opening. Future conflict exists if a tooling choice cannot satisfy local-only execution, stage inspectability, or the chapter-contiguous proving scope.
- Allowed transformation types: create the first active plan/tracker pair; define the proof contract and staging expectations; define the future sample qualification seam; sequence the future tooling decision; record affected and non-affected surfaces.
- Affected surfaces: the implementation-01 active bundle contents; the stated proving contract for the first runtime slice; the planning use of the existing PDF, PNG, and markdown root surfaces; future runtime sequencing expectations.
- Non-affected surfaces: runtime code; tests; artifact schema detail; provider selection; storage; auth; deployment; downstream integrations; archived bundles; project-spec invariants.
- Admissibility checks:
  - pass: the plan keeps tooling choice deferred until after proof contract and sample-gate seams.
  - pass: sample selection is not treated as solved.
  - pass: the first runtime slice explicitly includes PDF-to-PNG conversion before visual extraction.
  - pass: all four stages and both terminal artifacts remain explicit.
  - pass: no provenance, uncertainty, or canonical-fidelity rule is weakened.
- Stop conditions: stop if opening the bundle would silently amend the two-artifact contract, the four-stage model, provenance or uncertainty requirements, local-only posture, or chapter-contiguous proof scope; stop if tooling is selected before Seams 1 and 2 exist.

## Planned Seams

1. Proof contract and staging expectations
   Define the first honest runtime slice, its user-facing proof question, stage boundaries, stage evidence expectations, and terminal outputs. Record that runtime begins from PDF input and performs PDF-to-PNG conversion before visual extraction because PNG is the downstream working surface. Record the current source shape as two-page scanned spreads so later runtime work evaluates spread handling explicitly rather than assuming page-perfect single-page inputs.

2. Sample qualification gate
   Define what a qualifying proof sample must contain for honest runtime claims: scanned annotated PDF pages, chapter-contiguous coverage, representative markings, and at least one uncertainty case. Defer exact sample identity and exact qualification wording until runtime wiring is ready; require this seam to close before runtime proof claims.

3. Tooling and runtime selection
   Only after Seams 1 and 2 exist, choose local rasterization, OCR or vision, layout, and CLI wiring options against the recorded proof contract and sample gate. Keep provider choice subordinate to provenance, uncertainty visibility, stage inspectability, and local-only execution.

## CLI Proof Contract

Purpose statement for the first proof run: demonstrate that one local-only CLI batch run can start from a scanned chapter slice in PDF form, preserve the current two-page spread source layout as declared input context, retain inspectable evidence across prep and runtime stages, and emit two independent markdown artifacts without hiding uncertainty or normalizing away source ambiguity.

Provisional command shape:

```text
novel-extract prove \
   --pdf-input <path-to-source.pdf> \
   --source-selection <operator-selected-spread-range-or-page-range> \
   --output-root <path-to-run-root> \
   --run-label <short-run-id> \
   --keep-stage-evidence \
   --scan-layout two-page-spreads
```

Required contract-level inputs and flags:

- `--pdf-input`: required PDF ingress for the proof run.
- `--source-selection`: required operator-declared spread or logical page selection for the proof sample; must represent a chapter-contiguous slice even when numeric ids are still operator-discovered.
- `--output-root`: required run-scoped root for terminal artifacts and retained evidence.
- `--run-label`: required human-meaningful run id or label for proving, comparison, and operator notes.
- `--keep-stage-evidence`: required retention switch for prep output and each runtime stage output; the proof contract is not satisfied without inspectable evidence.
- `--scan-layout two-page-spreads`: required declaration of the current source layout so the proof does not assume clean single-page scans.

Required outputs:

- One markdown artifact for chapter-contiguous reconstructed novel text with visible provenance and visible uncertainty.
- One markdown artifact for extracted highlights, notes, and annotation interpretations with visible provenance and visible uncertainty.
- Retained prep evidence and retained per-stage runtime evidence under the run root.

Required evidence layout for the proof run:

```text
<output-root>/<run-label>/
   prep/
      pdf-to-png/
         ... rasterized spread images derived from the selected PDF slice
   stage-1-visual-extraction/
      ... inspectable extraction evidence from the PNG working surface
   stage-2-structural-reconstruction/
      ... inspectable chapter/page ordering and reconstruction evidence
   stage-3-annotation-interpretation/
      ... inspectable highlight and marginalia interpretation evidence
   stage-4-artifact-synthesis/
      ... inspectable artifact-assembly evidence
   outputs/
      novel-reconstruction.md
      annotation-extraction.md
```

Evidence rule: `prep/pdf-to-png/` is required retained preparation evidence because PNG is an allowed internal working surface, but it is not itself one of the four truth-claim runtime stages. The four runtime stages remain explicit and independent from prep.

Success conditions for the proof run:

- The run accepts PDF ingress plus an operator-declared chapter-contiguous source selection and declared two-page spread layout.
- The run retains prep evidence and retained evidence for all four runtime stages.
- The run emits both markdown artifacts in the same run without collapsing them into one artifact.
- The run preserves typed provenance and visible uncertainty rather than silently repairing ambiguous structure or annotations.
- The run keeps the contract at proof level only; it does not imply a stable public API, provider choice, or final markdown field wording.

Failure conditions for the proof run:

- Any run that skips retained prep evidence or any of the four retained runtime stage evidence surfaces.
- Any run that emits only one markdown artifact or merges the two artifact roles together.
- Any run that assumes single-page clean scans instead of honoring the declared two-page spread layout.
- Any run that hides uncertainty, strips provenance, or normalizes source ambiguity away by default.
- Any run description that depends on provider choice, stable API promises, or final artifact wording not yet approved.

Acceptance probe mapping for this CLI proof:

- Mixed annotations: the selected source packet must exercise highlight and annotation interpretation through Stage 3 and the annotation markdown artifact.
- Layout fidelity: the selected source packet must preserve chapter-contiguous ordering and spread-aware structure through prep, Stage 1, and Stage 2.
- Uncertainty honesty: ambiguous or degraded source cases must remain explicit in retained evidence and both markdown outputs when relevant.
- Artifact independence: one proof run must emit two independent markdown artifacts with separate roles, not one blended document.

## Test Packet To Hunt Down

Primary packet to go find for the first proof run: 4 contiguous scanned spreads from one chapter, equivalent to 8 logical book pages, all from a single uninterrupted chapter slice in the source PDF.

Required roles inside that 4-spread packet:

- 1 spread that is mostly clean running body text with no meaningful annotation, to anchor baseline reconstruction.
- 1 spread with at least one clear highlight or underline spanning more than a short isolated phrase, to prove annotation capture against body text.
- 1 spread with marginalia, symbols, brackets, or another non-inline annotation shape, to force interpretation beyond plain highlighting.
- 1 spread containing at least one honest uncertainty case such as faint marking, skew, gutter loss, bleed-through, or ambiguous chapter/layout structure, to prove visible uncertainty rather than silent repair.

Packet rules:

- The 4 spreads must be contiguous in source order and belong to one chapter slice.
- Reuse is allowed when one spread satisfies multiple roles, but the packet still has to contain all four roles across the 4 contiguous spreads.
- The operator must record the actual numeric spread ids or logical page ids only after visually hunting the packet down in the PDF; this plan does not invent those ids.

Fallback if one 4-spread packet cannot satisfy every role in a single chapter-contiguous slice:

- Packet A: 2 contiguous spreads from one chapter containing the clean-text baseline role and the highlight-or-underline role.
- Packet B: 2 contiguous spreads from the nearest available chapter-contiguous slice containing the marginalia-or-symbol role and the uncertainty role.

Fallback constraint: the first proof should still prefer one primary packet. The fallback exists only so operator page hunting can proceed without inventing numeric ids that repo evidence cannot justify.

## Non-Goals

- Do not select a provider or library stack yet.
- Do not define final markdown field wording or artifact schema details yet.
- Do not choose or process a concrete sample yet.
- Do not build runtime, tests, or automation in this opening step.
- Do not relax canonical fidelity with semantic normalization or hidden repair.

## Acceptance Criteria

- The bundle opening records the first proving contract as local-only, CLI batch, scanned annotated PDF input, with explicit PDF-to-PNG conversion before downstream processing.
- The bundle opening records the four stages and two independent markdown artifacts as fixed expectations for future implementation.
- The plan contains a proof-level CLI contract that keeps prep evidence separate from the four runtime stages, without choosing tooling or final artifact field wording.
- The plan defines an exact test packet to hunt down by count and role, while leaving actual numeric spread or page ids as operator work.
- The bundle opening records sample qualification as deferred but mandatory before runtime proof, without making sample choice the immediate purpose of implementation-01.
- The bundle opening orders future work so tooling choice occurs only after proof contract and sample-gate seams are defined.
- Approval gates remain unchecked because opening this bundle does not itself cross schema, API, auth, storage, deployment, destructive, or broad-architecture boundaries.

## Current Repo Runtime State

- No runtime code, CLI path, or stage wiring exists yet.
- The first active implementation bundle exists and is currently planning-only.
- The configured roots already distinguish PDF source, PNG working files, and markdown outputs.
- The current PDF source is expected to contain two-page scanned spreads rather than clean single-page captures.
- PDF is the existing configured source surface.
- The proof-level CLI contract is now recorded in this bundle, but no live runtime path implements it yet.
- No sample qualification gate or tooling choice has been recorded yet.

## Assumptions And Unknowns

- Assumption: the first honest proof remains local-only and batch-oriented.
- Assumption: rasterized PNG pages will be the downstream working surface even though PDF remains the ingress format.
- Unknown: which local rasterization, OCR or vision, and layout stack best satisfies inspectability and evidence retention.
- Unknown: whether the first runtime path should split spreads before visual extraction or treat spread handling inside the visual extraction stage.
- Unknown: which concrete numeric spread ids or logical page ids in the source PDF satisfy the defined test packet roles.
- Unknown: exact inline markdown field wording, as long as typed provenance and visible uncertainty remain mandatory.
- Unknown: whether one qualifying sample is enough for both artifact proofs or whether runtime proof will need a small set.

## Affected and Non-Affected Surfaces

- Affected: the first active implementation bundle contents; the proving contract for the first runtime slice; the future ordering of runtime work; the planning use of the existing PDF, PNG, and markdown root surfaces.
- Non-affected: project-spec invariants; runtime code and tests; provider integrations; storage systems; deployment surfaces; auth; downstream consumers; archived implementation history.

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