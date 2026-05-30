# Implementation 01 Plan

## Intent

Carry the first active implementation bundle through proof-contract and sample-qualification planning, without choosing tooling or building runtime yet.

Delivery posture: define the first honest runtime contract as local-only, CLI batch, scanned annotated pages first, chapter-contiguous reconstruction first, with PDF as ingress and an explicit PDF-to-PNG page conversion step before downstream processing.

The current source shape is a scanned PDF rendered as two-page spreads from a facedown photocopier workflow. Implementation-01 records that shape as an input constraint for the proof contract without yet choosing a split, crop, or rectification strategy.

Observed evidence: there is no runtime yet, and the configured roots already distinguish PDF source, PNG working files, and markdown outputs.

The supplied Schopenhauer packet is now the qualified implementation-01 sample by operator-observed evidence: PDF pages 20-28 and book pages 47-61 inside the configured whole-book PDF. That closes sample qualification for planning purposes while leaving tooling choice, runtime execution, and any narrower first-run sub-range deferred.

## Admissibility Report

- Invariant constraints: preserve two independent markdown terminal artifacts; preserve the four explicit stages of visual extraction, structural reconstruction, annotation interpretation, and artifact synthesis; preserve canonical non-normalization by default; preserve typed provenance and visible uncertainty; preserve local-only first proof, scanned annotated pages first, CLI batch first, and chapter-contiguous reconstruction first.
- Task constraints: keep implementation-01 at planning level; close the sample qualification gate truthfully from operator-observed evidence; treat PDF as the input format; make PDF-to-PNG conversion explicit in the first runtime slice; do not implement runtime or choose tooling in this seam-closing step.
- Constraint conflicts: none at bundle opening. Future conflict exists if a tooling choice cannot satisfy local-only execution, stage inspectability, or the chapter-contiguous proving scope.
- Allowed transformation types: maintain the active plan/tracker pair; define the proof contract and staging expectations; convert the generic packet definition into a formal sample qualification gate using the supplied Schopenhauer pages; sequence the future tooling decision; record affected and non-affected surfaces.
- Affected surfaces: the implementation-01 active bundle contents; the stated proving contract for the first runtime slice; the planning use of the existing PDF, PNG, and markdown root surfaces; future runtime sequencing expectations.
- Non-affected surfaces: runtime code; tests; artifact schema detail; provider selection; storage; auth; deployment; downstream integrations; archived bundles; project-spec invariants.
- Admissibility checks:
   - pass: the plan records the selected packet as the Schopenhauer PDF pages 20-28 and book pages 47-61 by operator-observed evidence only.
   - pass: the plan keeps tooling choice deferred until after the proof contract and qualified sample gate exist.
  - pass: the first runtime slice explicitly includes PDF-to-PNG conversion before visual extraction.
  - pass: all four stages and both terminal artifacts remain explicit.
   - pass: no runtime proof or stable API claim is implied by closing the sample gate.
  - pass: no provenance, uncertainty, or canonical-fidelity rule is weakened.
- Stop conditions: stop if the seam would silently amend the two-artifact contract, the four-stage model, provenance or uncertainty requirements, local-only posture, or chapter-contiguous proof scope; stop if the sample gate wording implies runtime success, chooses tooling, locks a stable API, or invents page facts not supplied by the operator.

## Planned Seams

1. Proof contract and staging expectations
   Define the first honest runtime slice, its user-facing proof question, stage boundaries, stage evidence expectations, and terminal outputs. Record that runtime begins from PDF input and performs PDF-to-PNG conversion before visual extraction because PNG is the downstream working surface. Record the current source shape as two-page scanned spreads so later runtime work evaluates spread handling explicitly rather than assuming page-perfect single-page inputs.

2. Sample qualification gate
   Define what a qualifying proof sample must contain for honest runtime claims: scanned annotated PDF pages, chapter-contiguous coverage, representative markings, and at least one uncertainty case. This seam is now closed by the supplied Schopenhauer packet at PDF pages 20-28 and book pages 47-61, recorded as operator-observed evidence only. A smaller executable sub-range may still be chosen later from inside this qualified packet.

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

## Sample Qualification Gate

Purpose statement for Seam 2: fix one truthful implementation-01 sample packet before tooling or runtime selection, using operator-observed evidence only.

Gate pass criteria:

- The sample lives inside the configured Schopenhauer whole-book PDF.
- The packet is contiguous in PDF order and book order and is recorded with exact page spans.
- The packet covers the proof roles required by the CLI contract: clean running text, highlight or underline evidence, non-inline annotation evidence, and at least one explicit uncertainty or degradation case.
- The packet qualification remains proof-level only: it does not count as runtime proof, extraction success, or tooling validation.
- A smaller first executable sub-range may later be selected only from inside this qualified packet.

Gate status: pass.

Gate evidence basis:

- Qualified packet: Schopenhauer whole-book PDF, PDF pages 20-28, book pages 47-61.
- Operator report: the packet is contiguous and contains everything previously requested for the proof sample.
- Clean spread with no annotations: PDF page 28, book pages 60-61.
- Clear highlights: multiple spreads inside the qualified packet.
- Clear underlines: multiple spreads inside the qualified packet.
- Marginalia: PDF page 20, book page 47.
- Ambiguity case: PDF page 24, book page 54, where the top of the circle could be mistaken as underlining the line above.
- Bleed-through case: PDF page 25, book page 56.

Limit of claim: this gate records sample qualification only. No runtime proof, extraction success, tooling choice, or stable API claim exists yet.

## Qualified Sample Packet

Selected implementation-01 packet:

- Source PDF: the configured Schopenhauer whole-book PDF.
- Packet span: PDF pages 20-28.
- Book span: pages 47-61.
- Qualification basis: operator-observed evidence only; no runtime execution has tested this packet yet.

Coverage map inside the qualified packet:

- Baseline reconstruction anchor: PDF page 28, book pages 60-61, clean spread with no annotations.
- Highlight coverage: multiple spreads inside the qualified packet contain clear highlights.
- Underline coverage: multiple spreads inside the qualified packet contain clear underlines.
- Marginalia anchor: PDF page 20, book page 47.
- Ambiguity anchor: PDF page 24, book page 54, where the top of the circle could be mistaken as underlining the line above.
- Degradation anchor: PDF page 25, book page 56, with bleed-through.

Selection note: Seam 2 fixes the outer qualified packet and its role coverage now. Seam 3 may still choose a smaller executable sub-range from inside PDF pages 20-28 and book pages 47-61 if that produces a sharper first runtime proof.

## Non-Goals

- Do not select a provider or library stack yet.
- Do not define final markdown field wording or artifact schema details yet.
- Do not execute runtime against the qualified sample yet.
- Do not build runtime, tests, or automation in this opening step.
- Do not relax canonical fidelity with semantic normalization or hidden repair.

## Acceptance Criteria

- The active bundle records the first proving contract as local-only, CLI batch, scanned annotated PDF input, with explicit PDF-to-PNG conversion before downstream processing.
- The active bundle records the four stages and two independent markdown artifacts as fixed expectations for future implementation.
- The plan contains a proof-level CLI contract that keeps prep evidence separate from the four runtime stages, without choosing tooling or final artifact field wording.
- The plan contains a formal sample qualification gate that records the selected Schopenhauer packet as PDF pages 20-28 and book pages 47-61, with role coverage grounded in operator-observed evidence.
- The plan keeps explicit that no runtime proof has been executed yet and that Seam 3 may still choose a smaller executable sub-range inside the qualified packet.
- The active bundle orders future work so tooling choice occurs only after proof contract and sample-gate seams are defined.
- Approval gates remain unchecked because this bundle still does not cross schema, API, auth, storage, deployment, destructive, or broad-architecture boundaries.

## Current Repo Runtime State

- No runtime code, CLI path, or stage wiring exists yet.
- The first active implementation bundle now records the proof contract and the qualified sample gate, but remains planning-only.
- The configured roots already distinguish PDF source, PNG working files, and markdown outputs.
- The current PDF source is expected to contain two-page scanned spreads rather than clean single-page captures.
- PDF is the existing configured source surface.
- The qualified implementation-01 packet is the Schopenhauer PDF pages 20-28 and book pages 47-61, recorded from operator-observed evidence only.
- The proof-level CLI contract is now recorded in this bundle, but no live runtime path implements it yet.
- No runtime proof has been executed yet, and no tooling choice has been recorded yet.

## Assumptions And Unknowns

- Assumption: the first honest proof remains local-only and batch-oriented.
- Assumption: rasterized PNG pages will be the downstream working surface even though PDF remains the ingress format.
- Assumption: the operator-observed Schopenhauer packet is sufficient to evaluate tooling choices before any executable proof is attempted.
- Unknown: which local rasterization, OCR or vision, and layout stack best satisfies inspectability and evidence retention.
- Unknown: whether the first runtime path should split spreads before visual extraction or treat spread handling inside the visual extraction stage.
- Unknown: whether the first executable proof should use the full qualified packet or a smaller sub-range inside PDF pages 20-28 and book pages 47-61.
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