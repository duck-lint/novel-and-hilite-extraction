## Project Thesis

- What the system is: A pipeline that ingests annotated book material and emits two independent markdown artifacts as terminal outputs: a Highlight Semantics Artifact for human semantic interaction with marked passages, and a Canonical Reconstruction Artifact for structurally faithful recovery of source text.
- What the system is not: It is not a downstream note-sync adapter, summary engine, theme extractor, or archival facsimile generator that hides uncertainty behind polished prose. The existence of either artifact must not depend on assumptions about later retrieval, storage, or processing systems.
- Why this project should exist: Annotated books contain two different forms of value that should not be collapsed into one output: the reader's marked semantic touchpoints and the source text's recoverable canonical structure. Separating those outputs keeps semantic usefulness from mutating reconstruction fidelity.
- Authoritative source, substrate, or real-world boundary the system must respect: The authoritative substrate is the ingested annotated book material itself, including visible text, layout, page boundaries, and reader markings. Semantic plausibility must not overwrite uncertain source reconstruction without provenance annotation.

## Desired User Outcomes

- Primary users or operators: A reader, researcher, or operator processing annotated books who needs both a usable semantic highlights document and a faithful reconstructed text document.
- Highest-value workflow: Ingest a marked book sample, run the pipeline once, and receive two standalone markdown artifacts that can each be read on their own without hidden dependency on a later system.
- What the user should be able to do: Review contextually resolved highlights with explicit commentary space; inspect a reconstructed source text with chapter and paragraph continuity; compare uncertain spans against provenance and confidence fields; and decide whether ambiguity is recoverable or irrecoverable.
- What the user should be able to inspect, verify, or understand: Which page or source region produced each output segment; whether text was directly extracted, inferred structurally, or semantically expanded; extraction confidence; reconstruction confidence; annotation interpretation confidence; and where the pipeline preserved ambiguity instead of forcing a clean answer.
- What would make the result feel genuinely useful rather than merely plausible: The Highlight Semantics Artifact must read cleanly enough for real engagement while staying honest about uncertainty, and the Canonical Reconstruction Artifact must preserve structural fidelity closely enough that a user can trust ordering, hierarchy, paragraphing, and formatting semantics without wondering where the system rewrote the book.

## Non-Goals

- Do not build: A thematic summarizer, author-intent interpreter, generic OCR cleanup pipeline, note-taking integration layer, or a single blended artifact that mixes semantic interpretation with canonical reconstruction.
- Do not fake via scaffolding, fixtures, mocks, dry runs, or structure alone: Claims about highlight resolution, paragraph reconstruction, page association, or artifact fidelity without real runtime evidence flowing from ingested annotated material.
- Do not smooth over ambiguity, uncertainty, or missing evidence with polished wording: Recoverable uncertainty must remain explicit, and irrecoverable uncertainty must remain visible as missing or unreadable rather than silently repaired.
- Do not preserve legacy behavior, donor-code assumptions, or compatibility shims unless explicitly required: The project should not inherit prior normalization habits such as modernizing punctuation, normalizing spelling, collapsing whitespace stylistics, rewriting dialogue formatting, removing repeated line breaks, or imposing semantic normalization on the canonical artifact unless explicitly configured and provenance-marked.

## Architectural Shape

- Required runtime surfaces or layers: Four explicit stages with separate truth claims and confidence properties. Visual Extraction: claim "these glyphs and markings were visually detected"; failure mode bad recognition; invariant avoid hallucinated text. Structural Reconstruction: claim "these detected elements form ordered paragraphs, headers, quotations, and page associations"; failure mode incorrect layout inference; invariant preserve canonical ordering and hierarchy. Annotation Interpretation: claim "this marking refers to this textual span or nearby context"; failure mode false attribution of intent or span; invariant preserve ambiguity when confidence is insufficient. Artifact Synthesis: claim "these markdown outputs conform to their artifact schemas"; failure mode structural inconsistency or provenance loss; invariant deterministic formatting and provenance preservation.
- Required source/evidence boundaries: The canonical artifact may only use directly extracted text plus explicitly labeled structural inference required to recover order and layout. The highlight artifact may semantically expand a marked fragment into sufficient surrounding sentence or paragraph context, but it may not infer thematic meaning, summarize author intent, rewrite prose, or normalize stylistic wording.
- Required inspectability surfaces: Per-stage outputs or logs that let an operator inspect raw extraction, structural grouping, annotation-to-span mapping, confidence values, and final artifact rows or sections with provenance typing.
- External systems, providers, or storage assumptions: OCR, vision, or layout tooling may be used, but no provider-specific behavior is authoritative unless surfaced through inspectable evidence. The terminal contract is the production of two markdown artifacts; downstream databases, embeddings, or publishing systems are optional and non-authoritative.
- Forbidden or deferred surfaces: Hidden semantic post-processing of the canonical artifact, downstream-dependent artifact schemas, auto-generated commentary text, silent repair of missing content, and any interface that implies certainty beyond the evidence actually present.
- First honest vertical slice that would prove the direction: Run a small annotated-book sample through all four stages and emit both markdown artifacts with page provenance, confidence typing, visible uncertainty markers, a blank commentary field for each highlight entry, and enough preserved structure to verify chapter and paragraph continuity.

## Runtime and Implementation Discipline

- What must exist as real runtime behavior: Real ingestion of annotated book material; explicit classification of annotation forms such as full highlight, underline, fragment, symbol, or other visible marking; contextual resolution of partial highlights; structurally faithful source reconstruction; emission of two independent markdown outputs; and provenance typing that records source page, extraction confidence, reconstruction confidence, annotation interpretation confidence, and whether text is directly extracted, inferred structurally, or semantically expanded.
- What counts as meaningful progress: A runtime path that preserves the separation between semantic interaction and canonical reconstruction, keeps uncertainty classes explicit, and produces inspectable outputs that a human can audit back to source pages and intermediate decisions.
- What must be visible before synthesis, automation, or UX claims are trusted: Recoverable uncertainty versus irrecoverable uncertainty must be explicit. Recoverable uncertainty includes low OCR confidence, ambiguous underline span, and uncertain page boundary. Irrecoverable uncertainty includes cropped page, unreadable markup, and missing content. The system must show where each uncertainty arose and what transformations remained admissible at that stage.
- Approval-sensitive surfaces: Changes to artifact schemas; provenance field definitions; the interpretive authority boundary between context expansion and semantic inference; normalization policy for canonical reconstruction; external API or storage commitments; and any change that lets semantic plausibility rewrite uncertain source text.
- Downstream fixtures, samples, or dependent roles that must remain truthful: Any demo corpus, fixture, example output, or dependent automation must preserve whether passages were directly extracted, structurally inferred, semantically expanded, or left unresolved. No sample should imply recovered text or confident interpretation where the runtime did not actually achieve it.

## Project Quality Bar

- UX qualities the system must preserve: Clear separation between the two artifact purposes; readable semantic highlight entries without overstated interpretation; faithful reconstructed text structure; explicit empty commentary space for user-authored reflection; and stable, deterministic markdown formatting.
- Evidence, provenance, or citation expectations: Every highlight entry and reconstructed segment should preserve page association where available and expose provenance fields for source page, extraction confidence, reconstruction confidence, annotation interpretation confidence, and transformation type. Provenance must distinguish direct extraction, structural inference, and semantic expansion rather than flattening them into a generic citation label.
- Retrieval, orchestration, or runtime inspectability expectations: Operators should be able to inspect stage boundaries, mutation permissions, and confidence drops. Artifact synthesis must not hide the earlier stages' uncertainty classes or silently upgrade confidence.
- Verification expectations: Verification must exercise the real runtime on annotated material and inspect both artifacts plus stage evidence. The canonical artifact should be checked for chapter hierarchy, paragraph boundaries, page continuity, quotation and formatting preservation where recoverable, and explicit markers where reconstruction becomes uncertain or impossible. The highlight artifact should be checked for annotation-form distinction, context expansion discipline, ambiguity preservation, and commentary-space presence.
- Operator expectations, especially for novice users: The system should make truth boundaries legible. A novice operator must be able to see what the pipeline knows, what it infers, what it expands for readability, and what it cannot recover, without needing to reverse-engineer model behavior or internal heuristics.

## Acceptance Probes

- Probe name: Highlight Semantics Artifact on mixed annotations
- User-facing question it answers: Can the pipeline turn a page containing highlights, underlines, fragments, and symbols into a readable semantic artifact without overstating interpretation?
- Minimum real runtime path it must exercise: Visual extraction of text and markings, annotation-form classification, ambiguous-span handling, contextual expansion for partial highlights, and synthesis of the highlight markdown artifact.
- Evidence that should be inspectable or saved: Final markdown artifact; per-entry provenance and confidence fields; visible annotation-form labels; blank commentary fields; and intermediate mapping from marking to resolved text span or ambiguity note.
- What does not count as proof: A manually curated markdown example, a highlight list without provenance typing, or a clean rewrite that removes ambiguity from fragmentary marks.

- Probe name: Canonical Reconstruction Artifact with layout fidelity
- User-facing question it answers: Can the pipeline reconstruct a chapter or page sequence into markdown that preserves hierarchy, paragraph boundaries, ordering, quotations, and formatting semantics where recoverable?
- Minimum real runtime path it must exercise: Visual extraction, structural reconstruction of headings and paragraphs, page association capture, and synthesis of the canonical markdown artifact without semantic normalization.
- Evidence that should be inspectable or saved: Final markdown artifact; page associations; structural grouping evidence; confidence values for reconstructed regions; and explicit markers for uncertain or missing segments.
- What does not count as proof: OCR text dumped into markdown, normalized prose that hides original formatting behavior, or a reconstruction that silently fills gaps.

- Probe name: Uncertainty boundary honesty
- User-facing question it answers: Does the system clearly distinguish recoverable from irrecoverable uncertainty and refuse unauthorized repair?
- Minimum real runtime path it must exercise: Processing of at least one low-confidence span, one ambiguous underline or page boundary, and one irrecoverable defect such as cropped or unreadable content through to final artifacts.
- Evidence that should be inspectable or saved: Stage-level uncertainty annotations, provenance fields showing confidence by stage, final artifact markers showing unresolved versus missing content, and operator-visible notes explaining why a transformation stopped.
- What does not count as proof: Generic confidence numbers without stage meaning, suppressed missing-content markers, or silently reconstructed text where the source was irrecoverable.

- Probe name: Artifact independence
- User-facing question it answers: Are the two markdown artifacts genuine terminal outputs rather than one artifact derived from assumptions about a downstream consumer or from the other artifact?
- Minimum real runtime path it must exercise: Full pipeline execution that emits both artifacts from shared evidence while preserving separate synthesis rules and schemas.
- Evidence that should be inspectable or saved: Both markdown artifacts from the same run; synthesis rules showing different allowed transformations; and stage records demonstrating that canonical reconstruction does not borrow semantic normalization from highlight synthesis.
- What does not count as proof: A single output split after the fact, a downstream-export adapter, or a canonical artifact whose wording was cleaned up using highlight-oriented heuristics.

## Open Questions To Clarify When They Matter

- Decision that would materially change the next implementation directive: v1 targets scanned annotated pages first, with chapter-contiguous reconstruction as the proving scope rather than page-local output only or whole-book continuity.
- Safe corpus, dataset, or sample for early probes: A private local sample under project control with visible chapter structure, multiple annotation forms, at least one ambiguous mark, and at least one intentionally damaged or cropped region to exercise irrecoverable uncertainty.
- External-call, privacy, mutation, or deployment constraints: Early development is local-only for OCR and vision execution. Material should remain local during early probes, and full stage evidence should be retained on every run.
- First interface surface to prove: A CLI batch pipeline that ingests a scanned annotated sample and emits the two markdown artifacts plus inspectable stage evidence.
- Unknown that is acceptable to defer for now: Exact field wording within the inline markdown schema, local provider selection, and whether later tooling will consume the artifacts, as long as provenance remains inline, confidence stays hybrid numeric plus categorical, and the two artifact contracts remain intact.

## Project References

- Companion governance primitives doc: `harness/project-spec/template-governance-primitives.md`
- Other project-spec docs in this folder: None yet beyond this spec and the companion governance primitives template.
