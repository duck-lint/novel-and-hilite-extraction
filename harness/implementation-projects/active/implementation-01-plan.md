# Implementation 01 Plan

## Intent

Carry the first active implementation bundle through the current live runtime seams using the approved local stack-1 path, while keeping the proof contract honest about the present implementation boundary: prep plus Stage 1 visual extraction, and Stage 2 structural reconstruction limited to ordered logical page units and bounded ordered block units.

Delivery posture: implement only local CLI prep plus stage-1 visual extraction and Stage 2 structural reconstruction against explicit PDF and page-range inputs, retain inspectable prep, OCR, logical-page, and block-unit evidence, and leave stages 3-4 plus the two markdown terminal artifacts as future work under the same proof contract.

The current source shape is a scanned PDF rendered as two-page spreads from a facedown photocopier workflow. The anchor packet also includes rotated spread rasters, so Implementation-01 must preserve the raw raster evidence while allowing explicit operator-declared rectification before spread splitting and OCR instead of assuming the raw width midpoint is already semantically page-aligned.

Observed evidence: there is now a live stage-1 runtime, a live spread-aware Stage 2 runtime at page-unit scope, and a bounded Stage 2 block-unit extension grounded only in retained OCR layout evidence. The configured roots already distinguish PDF source, PNG working files, and markdown outputs, and the PDF-page-28 anchor proved that splitting the unrectified raw spread at width midpoint produces sideways partial-page crops and garbage OCR instead of intent-satisfying whole-page evidence.

The supplied Schopenhauer packet is now the qualified implementation-01 sample by operator-observed evidence: PDF pages 20-28 and book pages 47-61 inside the configured whole-book PDF. That closes sample qualification for planning purposes while leaving tooling choice, runtime execution, and any narrower first-run sub-range deferred.

## Admissibility Report

- Invariant constraints: preserve two independent markdown terminal artifacts; preserve the four explicit stages of visual extraction, structural reconstruction, annotation interpretation, and artifact synthesis; preserve canonical non-normalization by default; preserve typed provenance and visible uncertainty; preserve local-only first proof, scanned annotated pages first, CLI batch first, and chapter-contiguous reconstruction first.
- Task constraints: keep claims at prep plus stage-1 visual extraction and Stage 2 structural reconstruction from retained Stage 1 OCR evidence; treat PDF as the input format; make PDF-to-PNG conversion explicit; keep controls generic for the scanned-novel object class; do not parse repo config in runtime code; do not claim stages 3-4 or final artifacts exist.
- Constraint conflicts: the active proof contract still names later stages and terminal artifacts as required future behavior, while the live implementation stops at Stage 2; later seams must preserve that distinction. Stage 3 remains blocked as an immediate next move until Stage 1 retains explicit marking observables. Older Stage 1 and Stage 2 validation roots created before spread rectification remain mechanically useful as evidence of prior behavior, but they are stale for intent-level claims about upright whole-page OCR on rotated spreads.
- Allowed transformation types: maintain the active plan/tracker pair; repair Stage 1 orientation handling at the root cause through explicit reusable controls; preserve the existing `page-units` and bounded `block-units` Stage 2 behaviors without editing Stage 2 unless compatibility breaks; retain raw prep evidence plus any rectified spread evidence needed for truthful lineage; use explicit Tesseract discovery with fallback; record validation evidence and affected surfaces truthfully.
- Affected surfaces: the implementation-01 active bundle contents; `novel_and_hilite_extraction/__main__.py`; `novel_and_hilite_extraction/stage1.py`; retained temp run roots used for rotated-anchor validation; the stated proving contract for the live runtime slices.
- Non-affected surfaces: `novel_and_hilite_extraction/stage2.py` unless Stage 1 compatibility forces a change; tests; artifact schema detail; provider selection; storage; auth; deployment; downstream integrations; archived bundles; project-spec invariants.
- Admissibility checks:
   - pass: the plan records the selected packet as the Schopenhauer PDF pages 20-28 and book pages 47-61 by operator-observed evidence only.
   - pass: the plan keeps tooling choice deferred until after the proof contract and qualified sample gate exist.
  - pass: the first runtime slice explicitly includes PDF-to-PNG conversion before visual extraction.
  - pass: all four stages and both terminal artifacts remain explicit.
   - pass: the live seams now claim only prep, stage-1 OCR evidence, and Stage 2 logical-page plus bounded block-unit reconstruction, not stages 3-4 or final markdown artifacts.
   - pass: no stable API, schema, deployment, or final-artifact claim is implied by the implemented stage-1 seam.
  - pass: no provenance, uncertainty, or canonical-fidelity rule is weakened.
- Stop conditions: stop if the seam would silently amend the two-artifact contract, the four-stage model, provenance or uncertainty requirements, local-only posture, or chapter-contiguous proof scope; stop if the sample gate wording implies runtime success, chooses tooling, locks a stable API, or invents page facts not supplied by the operator.

## Planned Seams

1. Proof contract and staging expectations
   Define the first honest runtime slice, its user-facing proof question, stage boundaries, stage evidence expectations, and terminal outputs. Record that runtime begins from PDF input and performs PDF-to-PNG conversion before visual extraction because PNG is the downstream working surface. Record the current source shape as two-page scanned spreads so later runtime work evaluates spread handling explicitly rather than assuming page-perfect single-page inputs.

2. Sample qualification gate
   Define what a qualifying proof sample must contain for honest runtime claims: scanned annotated PDF pages, chapter-contiguous coverage, representative markings, and at least one uncertainty case. This seam is now closed by the supplied Schopenhauer packet at PDF pages 20-28 and book pages 47-61, recorded as operator-observed evidence only. A smaller executable sub-range may still be chosen later from inside this qualified packet.

3. Tooling and runtime selection
   Only after Seams 1 and 2 exist, choose local rasterization, OCR or vision, layout, and CLI wiring options against the recorded proof contract and sample gate. Keep provider choice subordinate to provenance, uncertainty visibility, stage inspectability, local-only execution, and a reusable control surface for the scanned-novel object class rather than Schopenhauer-specific behavior. This seam is now partially realized by the first live runtime slice: `python -m novel_and_hilite_extraction stage1-visual-extract`.

4. Stage-2 structural reconstruction on spread-aware outputs
   Only after prep and Stage 1 can show explicit derived page surfaces from declared two-page spreads with retained lineage, open structural reconstruction on top of those derived surfaces. Preserve page association, ordering, and uncertainty lineage without claiming final markdown artifacts yet.
   This Stage 2 slice is now realized as `python -m novel_and_hilite_extraction stage2-structural-reconstruct`, with `page-units` preserving ordered logical page reconstruction from Stage 1 spread-aware OCR entries and `block-units` deepening that seam to ordered block reconstruction from blank-line-separated OCR line groups. The bounded block seam keeps page order first, then intra-page block order, and does not yet claim cross-page paragraph continuation, hierarchy, chapter boundaries, annotation interpretation, or final markdown artifacts.

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

Limit of claim: this gate records sample qualification only. Stage-1 runtime validation now exists against this packet, but full-pipeline proof, extraction success across later stages, tooling finality, and stable API claims still do not.

## Qualified Sample Packet

Selected implementation-01 packet:

- Source PDF: the configured Schopenhauer whole-book PDF.
- Packet span: PDF pages 20-28.
- Book span: pages 47-61.
- Qualification basis: operator-observed evidence fixed the packet; stage-1 runtime validation has now exercised this packet, but later stages remain unimplemented and untested.

Coverage map inside the qualified packet:

- Baseline reconstruction anchor: PDF page 28, book pages 60-61, clean spread with no annotations.
- Highlight coverage: multiple spreads inside the qualified packet contain clear highlights.
- Underline coverage: multiple spreads inside the qualified packet contain clear underlines.
- Marginalia anchor: PDF page 20, book page 47.
- Ambiguity anchor: PDF page 24, book page 54, where the top of the circle could be mistaken as underlining the line above.
- Degradation anchor: PDF page 25, book page 56, with bleed-through.

Selection note: Seam 2 fixes the outer qualified packet and its role coverage now. The default first executable proof should use the full qualified packet, PDF pages 20-28 and book pages 47-61. Seam 3 may narrow to a smaller executable sub-range only if tooling evaluation produces a grounded reason such as unacceptable runtime cost, unstable spread handling, or worse inspectability on the full packet.

## Seam 3 Control-Surface Rule

Purpose statement: the Schopenhauer packet is a proving specimen for the broader object class of scanned printed novel pages with reader annotations. Seam 3 must evaluate tooling by whether it exposes reusable controls for that object class, not by whether it can be tuned specifically for this one book.

Reusable control-surface expectations for the object class:

- Source selection control: operators can choose the PDF page or spread range without code changes.
- Scan-layout control: operators can declare single-page versus two-page spread input without changing runtime logic.
- Prep control: rasterization behavior such as DPI, color mode, and image format can be adjusted as run controls rather than book-specific code edits.
- Spread-handling control: splitting, cropping, or rectification behavior is selectable or configurable without hard-coding one book's geometry.
- OCR or vision control: model or engine choice, language settings, and sensitivity knobs are reusable run controls rather than title-specific branches.
- Layout and annotation control: paragraph grouping, page-order recovery, and annotation sensitivity can be tuned at the object-class level without naming Schopenhauer-specific assumptions.
- Evidence control: retained prep and stage evidence remain operator-selectable and run-scoped.

Overfit rejection criteria for Seam 3:

- Reject tooling approaches that require Schopenhauer-specific crop boxes, thresholds, page ids, typography assumptions, or annotation heuristics to become usable.
- Reject tooling approaches that collapse reusable controls into hidden code constants or one-off preprocessing steps.
- Reject tooling approaches whose inspectability depends on manual repairs that cannot be represented as explicit operator controls or retained evidence.

Acceptable claim boundary: a tooling recommendation from Seam 3 may say that a stack looks promising for the scanned-novel object class because it works against the qualified Schopenhauer packet without book-specific tuning. It may not claim the class is solved or that later books will require no additional control calibration.

## Seam 3 Tooling Scout

Observed local environment for implementation-01:

- Available now: Python 3.14, `numpy`, `pypdfium2`, `Pillow`, `opencv-python`, `pytesseract`, and installed Tesseract OCR.
- Installed Tesseract locations discovered during validation: `C:\Program Files\Tesseract-OCR\tesseract.exe` and `C:\Users\madis\AppData\Local\Programs\Tesseract-OCR\tesseract.exe`.

Current scout conclusion:

- PDF-to-PNG prep is available from the installed local stack through `pypdfium2`.
- OCR and image-processing support are available from the installed local stack through Tesseract OCR, `pytesseract`, `Pillow`, and `opencv-python`.
- There is no grounded reason yet to narrow below the full qualified packet. The current environment gap is about missing tooling, not about the packet being too broad.

Stack-1 selection and validation evidence:

- Selected first local stack: `pypdfium2` + `Pillow` + `opencv-python` + `pytesseract` + local Tesseract OCR.
- Dependency installation completed locally without repo-file changes.
- Smoke-test validation succeeded against the qualified Schopenhauer packet:
   - Rasterized PDF page 24 and PDF page 28 from the configured whole-book PDF into PNG images.
   - Generated raster size: 2550x3301 for both sampled pages.
   - Detected a working Tesseract binary at `C:\Program Files\Tesseract-OCR\tesseract.exe`.
   - OCR on clean anchor PDF page 28 succeeded with approximate text length 3958 and a short excerpt beginning with `19`.
- Persistent PATH visibility for bare `tesseract` across all shells was not confirmed in this turn, so the installed binary path remains the safest explicit reference until runtime wiring establishes its invocation method.

Provisional stack ranking for follow-up selection, assuming local-only execution and reusable object-class controls:

1. PDF rasterization library such as `pypdfium2` or `PyMuPDF` plus `opencv-python`, `Pillow`, and `Tesseract`-backed OCR.
   This best matches the desired control surface for spread handling, prep controls, inspectability, and printed-page OCR, but it requires local installation work before it can be validated here.

2. Poppler-backed rasterization such as `pdf2image` plus `opencv-python`, `Pillow`, and `Tesseract`-backed OCR.
   This can also fit the object class, but it depends on local Poppler utilities that are not present now.

3. Pure-Python OCR stack such as `PaddleOCR` or `Surya` plus a separate rasterizer and image-processing layer.
   This remains admissible as a local-only option, but it introduces more moving parts and is currently less grounded in the local environment than the first two paths.

Selection implication for Seam 3: the first local stack is now installed, minimally validated, and materialized as the first live runtime seam. The next truthful move is to extend the proof incrementally from this stage-1 base, not to claim that the full extraction pipeline already exists.

## Implemented Runtime Slices

Implemented Stage 1 command shape:

```text
python -m novel_and_hilite_extraction stage1-visual-extract \
   --pdf-input <path-to-source.pdf> \
   --page-range <pdf-page-selection> \
   --output-root <path-to-run-root> \
   --run-label <short-run-id> \
   --scan-layout <operator-declared-layout> \
   --spread-handling <auto|keep-whole|split-halves> \
   [--spread-rotation-deg <0|90|180|270>] \
   --dpi <render-dpi> \
   [--outer-crop-px <pixels>] \
   [--gutter-crop-px <pixels>] \
   [--top-crop-px <pixels>] \
   [--bottom-crop-px <pixels>] \
   [--tesseract-cmd <path-or-command>]
```

Implemented Stage 2 command shape:

```text
python -m novel_and_hilite_extraction stage2-structural-reconstruct \
   --run-root <existing-stage1-run-root> \
   --reconstruction-scope <page-units|block-units>
```

Current behavior boundary:

- The implemented runtime now covers prep plus Stage 1 visual extraction and bounded Stage 2 structural reconstruction only.
- `python -m novel_and_hilite_extraction stage1-visual-extract` rasterizes selected PDF pages into retained source-spread PNG prep evidence, derives page-aware surfaces from each spread through explicit reusable controls, and runs OCR over each derived surface.
- The Stage 1 command writes prep evidence under `prep/pdf-to-png/` and `prep/derived-surfaces/`, and writes stage-1 OCR evidence under `stage-1-visual-extraction/`, with manifests in those locations.
- Page selection stays explicit through `--page-range`, including simple comma and inclusive range combinations.
- Spread handling stays explicit through `--spread-handling`, with `auto` mapping declared `two-page-spreads` inputs to `split-halves` and other layouts to `keep-whole`.
- Spread rectification stays explicit through `--spread-rotation-deg`, interpreted as clockwise degrees applied before derived-surface cropping and OCR. When the flag is omitted, `two-page-spreads` default to 90 and other layouts default to 0; operators can still force no rotation with `--spread-rotation-deg 0`. The raw rasterized spread PNG is always preserved, and a rectified spread PNG is retained when rotation is non-zero so crop lineage stays truthful.
- Crop controls stay explicit through `--outer-crop-px`, `--gutter-crop-px`, `--top-crop-px`, and `--bottom-crop-px`.
- Tesseract resolution is explicit and reusable: honor `--tesseract-cmd` first, then PATH if available, then the fixed known-install order discovered during tooling validation.
- Prep manifests record raw source-spread entries, rectified source-spread entries when present, and derived-surface entries separately. Stage-1 manifests record OCR entries per derived surface with lineage back to the actual source spread used for cropping while still retaining the raw spread path.
- The stage-1 manifest records the selected Tesseract path, selection rule, candidate probes, selected pages, declared scan layout, resolved spread handling, requested and applied spread rotation, per-surface evidence paths, and OCR confidence summaries.
- `python -m novel_and_hilite_extraction stage2-structural-reconstruct --reconstruction-scope page-units` validates the retained spread-aware Stage 1 manifest, orders logical pages by `source_pdf_page` then `surface_order`, writes one retained logical-page text file per ordered page, and records Stage 1 lineage plus OCR confidence in `stage-2-structural-reconstruction/manifest.json`.
- `python -m novel_and_hilite_extraction stage2-structural-reconstruct --reconstruction-scope block-units` preserves the logical page ordering step, then segments each logical page deterministically into consecutive non-empty OCR line groups separated by blank lines, writes retained `block-unit-*.txt` evidence files in global order, and records block-to-page-to-surface lineage plus inherited uncertainty in the Stage 2 manifest.
- The Stage 2 manifest states the claim boundary explicitly: block reconstruction is layout-derived only, and cross-page paragraph continuation, hierarchy, chapter boundaries, annotation interpretation, and final markdown artifacts are not implemented in this seam.

## Implemented Stage 2 Slice

Implemented command shape:

```text
python -m novel_and_hilite_extraction stage2-structural-reconstruct \
   --run-root <path-to-existing-run-root> \
   [--reconstruction-scope <page-units|block-units>]
```

Current behavior boundary:

- The implemented Stage 2 slice consumes an existing `stage-1-visual-extraction/manifest.json` from a prior run root and requires spread-aware `split-halves` page surfaces with retained OCR text paths.
- The command validates that each Stage 1 page-unit entry still resolves to an existing source spread PNG, derived surface PNG, and OCR text file beneath the same run root.
- `--reconstruction-scope page-units` reconstructs ordered logical page units only by sorting explicit Stage 1 observables, `source_pdf_page` ascending and then `surface_order` ascending, while rejecting duplicate ordering keys.
- `--reconstruction-scope block-units` preserves that logical page ordering step, then segments each logical page deterministically into consecutive non-empty OCR line groups separated by blank lines.
- The command writes retained Stage 2 evidence under `stage-2-structural-reconstruction/` as one `logical-page-XXXX.txt` file per ordered page unit, plus `block-unit-XXXX.txt` evidence files when `block-units` is selected, together with a Stage 2 manifest.
- The Stage 2 manifest carries forward per-logical-page and per-block lineage to `source_pdf_page`, `surface_id`, `source_spread_png_path`, `derived_png_path`, and the Stage 1 OCR text path, together with upstream OCR confidence summaries and inherited uncertainty flags.
- The Stage 2 manifest states the claim boundary explicitly: the `block-units` seam is layout-derived only and does not yet model cross-page paragraph continuation, hierarchy, chapter boundaries, annotation interpretation, or final markdown artifacts.

Validation evidence for the first Stage 2 slice:

- Pre-rectification anchor validation against the existing page-28 split run root passed mechanically with exit code 0 and produced 2 logical-page text files plus a manifest, but it is stale for intent-level claims because the upstream OCR surfaces were malformed.
- Pre-rectification full-packet validation against the existing qualified packet run root passed mechanically with exit code 0 and produced 18 logical-page text files plus a manifest, but it is stale for intent-level claims because the upstream OCR surfaces were malformed.
- Pre-rectification anchor block-unit validation against the retained page-28 split run root passed mechanically with exit code 0 and produced 2 logical-page text files, 16 `block-unit-*.txt` files, and a manifest recording `reconstruction_scope` `block-units`, but it is stale for intent-level claims because the upstream OCR surfaces were malformed.
- Pre-rectification full-packet block-unit validation against the retained qualified packet run root passed mechanically with exit code 0 and produced 18 logical-page text files, 244 `block-unit-*.txt` files, and a manifest recording `block_unit_count` 244, but it is stale for intent-level claims because the upstream OCR surfaces were malformed.

Validation status for the live slice:

- Passed: fresh rotated-anchor run on PDF page 28 with `--spread-rotation-deg 90`, with 1 raw source spread PNG, 1 retained rectified spread PNG, 2 upright whole-page derived surface PNGs, and 2 readable OCR text files.
- Passed: narrow Stage 2 `page-units` compatibility rerun on that corrected anchor root, producing 2 logical-page text files and a Stage 2 manifest whose lineage points to the rectified source spread.
- Passed: fresh corrected full-packet run on PDF pages 20-28 with `--spread-rotation-deg 90`, with 9 raw source spread PNGs, 9 retained rectified spread PNGs, 18 upright whole-page derived surface PNGs, and 18 OCR text files.
- Passed: corrected full-packet Stage 2 rerun on that rectified root, producing 18 logical pages for `page-units`, then 18 logical pages plus 146 `block-unit-*.txt` files for `block-units`.
- Passed: fresh rotated-anchor run on PDF page 28 with no explicit rotation flag, using the layout default of 90 for `two-page-spreads`, with 1 raw source spread PNG, 1 retained rectified spread PNG, 2 upright whole-page derived surface PNGs, and readable OCR.
- Passed: fresh rotated-anchor opt-out run on PDF page 28 with `--spread-rotation-deg 0`, recording applied rotation 0 and emitting no rectified spread PNG so printed-page-style inputs can stay unrotated when required.
- Stale for intent-level claims: older pre-rectification anchor and full-packet run roots remain evidence of the prior malformed width-midpoint behavior and should not be cited as proof of correct rotated-spread handling.

## Non-Goals

- Do not implement later Stage 2 seams beyond bounded block-unit reconstruction, stages 3-4, or either final markdown artifact yet.
- Do not define final markdown field wording or artifact schema details yet.
- Do not parse repo config in runtime code or bake in Schopenhauer-specific heuristics.
- Do not add packaging, deployment, auth, storage, or stable public API commitments.
- Do not relax canonical fidelity with semantic normalization or hidden repair.

## Acceptance Criteria

- The active bundle records the first proving contract as local-only, CLI batch, scanned annotated PDF input, with explicit PDF-to-PNG conversion before downstream processing.
- The active bundle records the four stages and two independent markdown artifacts as fixed expectations for future implementation.
- The plan contains a proof-level CLI contract that keeps prep evidence separate from the four runtime stages, without choosing tooling or final artifact field wording.
- The plan contains a formal sample qualification gate that records the selected Schopenhauer packet as PDF pages 20-28 and book pages 47-61, with role coverage grounded in operator-observed evidence.
- The plan keeps explicit that live runtime validation now covers Stage 1 and bounded Stage 2 only, while the full four-stage proof and both markdown terminal artifacts remain unimplemented.
- The plan defines Seam 3 as object-class tooling evaluation and rejects Schopenhauer-specific heuristics as an admissible default.
- The plan records that the approved local-first stack is now installed and minimally validated against the qualified packet, and that no grounded reason exists yet to narrow below the full qualified packet.
- The active bundle orders future work so tooling choice occurs only after proof contract and sample-gate seams are defined.
- The repo root now contains a runnable `python -m novel_and_hilite_extraction stage1-visual-extract` surface for prep plus stage-1 OCR evidence only.
- The repo root now also contains a runnable `python -m novel_and_hilite_extraction stage2-structural-reconstruct` surface for ordered logical pages plus bounded ordered block units from retained Stage 1 OCR evidence.
- The implemented seam resolves Tesseract explicitly by override, PATH, then fixed known-install order, and records the selected path in retained manifests.
- The live seam has passed the required one-page anchor run and the full qualified-packet run with retained prep and stage-1 evidence.
- The live seam now operationalizes declared two-page spreads into explicit derived page surfaces with retained lineage and OCR confidence summaries.
- Stage 2 now exists as a live seam at ordered logical-page plus bounded ordered block-unit scope because spread-aware prep and Stage 1 outputs have been validated on both the anchor and full qualified packet.
- Approval gates remain unchecked because this bundle still does not cross schema, API, auth, storage, deployment, destructive, or broad-architecture boundaries.

## Current Repo Runtime State

- A repo-root package now provides `python -m novel_and_hilite_extraction stage1-visual-extract`.
- A repo-root package now also provides `python -m novel_and_hilite_extraction stage2-structural-reconstruct`.
- The runtime currently implements explicit page-range parsing, spread-aware derived surface generation, reusable Tesseract discovery, stage-1 OCR evidence manifests, ordered logical-page reconstruction, and bounded ordered block reconstruction from retained OCR layout evidence.
- Stages 3-4 and both final markdown artifacts do not exist yet.
- The configured roots already distinguish PDF source, PNG working files, and markdown outputs.
- The current PDF source is expected to contain two-page scanned spreads rather than clean single-page captures.
- PDF is the existing configured source surface.
- The qualified implementation-01 packet is the Schopenhauer PDF pages 20-28 and book pages 47-61, recorded from operator-observed evidence only.
- The proof-level CLI contract is now recorded in this bundle, and the live runtime currently implements the prep plus Stage 1 subset and a bounded Stage 2 subset of that contract.
- The first local tooling path is now selected and installed as `pypdfium2` + `Pillow` + `opencv-python` + `pytesseract` + local Tesseract OCR.
- A stack-level smoke test has been executed successfully, and the live runtime seams have also passed the one-page and full-packet spread-aware Stage 1 proof runs plus anchor and full-packet Stage 2 block-unit validation.

## Assumptions And Unknowns

- Assumption: the first honest proof remains local-only and batch-oriented.
- Assumption: rasterized PNG pages will be the downstream working surface even though PDF remains the ingress format.
- Assumption: the operator-observed Schopenhauer packet is sufficient to evaluate tooling choices and to anchor the first executable proof runs.
- Assumption: the Schopenhauer packet is a useful proxy for the broader scanned-novel object class, but not a license for book-specific runtime behavior.
- Unknown: whether the installed stack remains sufficient once runtime wiring reaches structural reconstruction, annotation interpretation, and full-packet evidence retention.
- Unknown: whether the current split-halves plus crop control surface is sufficient across later novels in the same object class or whether rectification controls will become necessary.
- Unknown: whether tooling evaluation will reveal a grounded reason to narrow the first executable proof below the full qualified packet.
- Unknown: which minimal reusable controls are sufficient across later novels in the same object class without creating a brittle operator surface.
- Unknown: whether Stage 2 should consume derived surfaces exactly as emitted from Stage 1 or whether it needs an additional page-association manifest layer first.
- Unknown: whether runtime wiring should call `tesseract` from PATH or preserve an explicit configured binary path for local robustness.
- Unknown: exact inline markdown field wording, as long as typed provenance and visible uncertainty remain mandatory.
- Unknown: whether one qualifying sample is enough for both artifact proofs or whether runtime proof will need a small set.

## Affected and Non-Affected Surfaces

- Affected: the first active implementation bundle contents; the proving contract for the first runtime slice; the repo-root runtime package; the future ordering of runtime work; the planning use of the existing PDF, PNG, and markdown root surfaces.
- Non-affected: project-spec invariants; tests; provider integrations; storage systems; deployment surfaces; auth; downstream consumers; archived implementation history.

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