# Governance Primitives

This file defines project-local authority semantics, approval boundaries, admissible transformations, and review scaffolding.

It is part of the project spec's invariant space. Use it to describe what implementation must preserve or explicitly amend, not to restate harness workflow prompts.

## Governance Posture

- Hard constraints the implementation must preserve: The system must emit two independent markdown artifacts as terminal outputs, one for highlight semantics and one for canonical reconstruction. Annotated book material is the authoritative substrate. Semantic plausibility must not overwrite uncertain source reconstruction without provenance annotation. The canonical artifact must preserve structure and must not perform semantic normalization by default. The highlight artifact may expand partial marks into sufficient local context, but it may not infer thematic meaning, summarize author intent, rewrite prose, or normalize stylistic wording. Recoverable and irrecoverable uncertainty must remain explicit.
- Observability scaffolding used to inspect those constraints: Inspectable per-stage outputs or logs for visual extraction, structural reconstruction, annotation interpretation, and artifact synthesis; typed provenance fields on final artifact entries or sections; stage-specific confidence values; visible markers for unresolved, missing, cropped, or unreadable regions; and run outputs that let an operator trace each artifact segment back to source pages and intermediate decisions.
- Distinctions that must remain explicit rather than hidden in prompts, chat history, or model intuition: Highlight semantics versus canonical reconstruction; direct extraction versus structural inference versus semantic expansion; recoverable versus irrecoverable uncertainty; source evidence versus derived structure versus synthesized presentation; and allowed context expansion versus forbidden interpretation.

## Invariant Authority

Use this order when deciding what the project is allowed to become:

1. Explicit amendments to the project spec or governance primitives approved by project authority.
2. This file and the other docs under `harness/project-spec/**`.
3. Open decisions that interpret the project spec without silently overriding it.
4. Active plans and trackers implementing an already-authorized objective.
5. Current user instructions selecting, sequencing, or pausing already-authorized work.
6. Archived implementation history and prior chat context.

Current instructions may choose work or explicitly amend the spec, but they do not silently override project invariants.

## Task Authority

Use this order when deciding what to do next inside the current invariant space:

1. Current user instruction for the present task.
2. Open decisions in `harness/open-decisions.md`.
3. Active implementation plan and tracker.
4. Relevant repo-local harness docs under `harness/`.
5. Archived implementation history and prior chat context.

If task authority conflicts with invariant authority, stop and surface the conflict instead of improvising around it.

## Approval Boundaries

Require explicit approval before crossing:

- Project spec or governance amendment: Any change to the two-artifact contract, the uncertainty taxonomy, the interpretive authority boundary, the four-stage runtime model, or the rule that semantic plausibility cannot silently repair uncertain reconstruction.
- Schema: Any change to artifact schemas, provenance field meanings, confidence field semantics, commentary-space requirements, or the distinction between direct extraction, structural inference, and semantic expansion.
- API: Any new interface commitment that changes the terminal output contract, requires downstream consumers, or obscures stage evidence needed to audit correctness.
- Auth: Any introduction of credentialed external services, user accounts, or access control, since none is currently authorized by the project spec.
- Storage: Any persistent storage beyond local artifact and evidence output, any retention policy that discards source-linked evidence, or any schema that makes downstream storage authoritative over the source material.
- Deployment: Any remote or cloud deployment requirement, background service architecture, or provider lock-in that changes privacy, evidence locality, or stage inspectability assumptions.
- Destructive operation: Any deletion, overwrite, or irreversible transformation of source images, annotations, stage evidence, or generated artifacts without preserving inspectable lineage.
- Broad architecture: Any collapse of the four explicit stages, any design that derives one artifact from the other instead of shared source evidence, or any hidden post-processing layer that mutates truth claims.
- Compatibility or fallback commitment: Any promise to support legacy normalized outputs, downstream-specific formats, or fallback behavior that weakens provenance, uncertainty visibility, or artifact independence.
- Project-intent-dependent behavior not already authorized by the project spec: Thematic tagging, summarization, author-intent inference, prose rewriting, silent cleanup of unreadable content, or canonical text normalization beyond what the spec explicitly allows.

## Invariants and Integrity Constraints

- Project truths that must remain stable: The highlight artifact exists for semantic interaction with marked material, not archival reconstruction. The canonical artifact exists for reconstruction fidelity, not semantic interpretation. The two artifacts are separate terminal outputs with separate synthesis rules. Structural fidelity outranks cosmetic readability in canonical reconstruction, and honesty about ambiguity outranks apparent completeness in both artifacts.
- Authoritative versus derived, operational, synthesized, or presentation material: Source pages, visible text, and visible annotations are authoritative. Visual extraction, structural reconstruction, annotation interpretation, and their confidence judgments are derived operational evidence. The final markdown artifacts are synthesized presentation outputs that remain subordinate to source-linked provenance and stage evidence.
- Fixture, sample, or test roles that must remain truthful: Samples, fixtures, and acceptance corpora must preserve whether passages were directly extracted, structurally inferred, semantically expanded, unresolved, or missing. They must not present manually repaired text as if the runtime recovered it.
- Compatibility promises, if any: The current compatibility promise is limited to producing inspectable markdown artifacts with typed provenance. There is no standing promise to preserve legacy normalization behavior, external API shape, or downstream import compatibility.
- Verification duties that must not be skipped: Real runtime execution on annotated material, inspection of both emitted artifacts, inspection of stage evidence, confirmation that uncertainty is preserved rather than erased, confirmation that canonical reconstruction does not borrow semantic normalization, and confirmation that provenance typing survives artifact synthesis.
- Unknowns, ambiguity, or uncertainty that must remain visible: Low OCR confidence, ambiguous underline span, uncertain page boundary, cropped page, unreadable markup, and missing content must remain visible in the evidence trail and in final artifacts where relevant. Unknowns must not be collapsed into confident text.

## Admissible Transformations

- Changes allowed without amending the project spec: Improving extraction or layout accuracy; refining confidence calibration; adding inspectability fields or stage logs; extending annotation-form detection while preserving existing authority limits; tightening deterministic markdown formatting; and improving operator-facing visibility of uncertainty without changing truth claims.
- Changes that require an open decision before proceeding: Choosing between local and external OCR or vision providers; deciding whether early slices prioritize born-digital, scanned, or mixed-source inputs; defining exact markdown field layouts when multiple truthful encodings are possible; and introducing optional configured normalization modes that remain outside the default canonical path.
- Changes that require explicit project-spec or governance amendment: Blending the two artifacts into one; making either artifact downstream-dependent; expanding interpretive authority beyond local context expansion; allowing canonical semantic normalization by default; removing commentary space from highlight outputs; changing the uncertainty taxonomy; or weakening provenance typing.
- Transformations that must preserve provenance, inspectability, or lineage: Any movement from source to extracted glyphs, from extracted glyphs to reconstructed structure, from markings to interpreted spans, and from stage evidence to final markdown must preserve source page association where available, stage-specific confidence, transformation type, and whether text is direct, structural, or semantic in origin.
- Transformations that are forbidden shortcuts: Hallucinating unreadable text, silently filling cropped or missing content, rewriting original prose for smoothness, flattening all confidence into a single opaque score, deriving canonical wording from semantic highlight output, and treating polished examples as evidence of real runtime capability.

## Review Checkpoints

- What should be visible before trusting source authority: The actual ingested annotated material or an inspectable safe sample, with enough page and markup visibility to ground later claims.
- What should be visible before trusting derived or operational evidence: Stage outputs showing detected glyphs and markings, structural grouping into chapters or paragraphs where applicable, annotation-to-span mappings, stage-specific confidence values, and explicit uncertainty classifications.
- What should be visible before trusting synthesis, automation, or UX claims: Both markdown artifacts produced from the same run, clear separation of their schemas and allowed mutations, typed provenance on final entries or sections, deterministic formatting behavior, and evidence that blank commentary fields and uncertainty markers survive synthesis.
- What should be visible before closing work as complete: Acceptance probes exercised on real annotated inputs, saved artifacts and evidence, no silent normalization of canonical reconstruction, no hidden semantic overwrite of uncertain source text, and no unresolved conflict between current work and the invariant boundaries above.

## Acceptance Probes

- Probe name: Source-to-canonical fidelity
- Question it answers: Does the system preserve chapter hierarchy, paragraph boundaries, ordering, page association, and recoverable formatting semantics without semantic cleanup?
- Required real runtime path: Ingest annotated pages, run visual extraction and structural reconstruction, then synthesize the canonical markdown artifact from source-linked evidence.
- Evidence that must be inspectable or saved: Canonical artifact output, structural reconstruction evidence, page association records, confidence values for reconstructed regions, and explicit markers for uncertain or missing segments.
- What does not count as proof: Plain OCR dumps, normalized prose with hidden edits, or reconstructions that silently fill gaps.

- Probe name: Annotation interpretation discipline
- Question it answers: Can the system resolve mixed annotation forms into useful highlight entries while staying inside the allowed interpretive boundary?
- Required real runtime path: Ingest marked pages, run visual extraction and annotation interpretation, resolve partial marks into local context where justified, and synthesize the highlight markdown artifact.
- Evidence that must be inspectable or saved: Highlight artifact output, annotation-form labels, blank commentary fields, marking-to-span mappings, annotation interpretation confidence, and explicit ambiguity markers where span resolution is uncertain.
- What does not count as proof: Theme summaries, rewritten excerpts, or outputs that replace ambiguity with confident prose.

- Probe name: Uncertainty taxonomy compliance
- Question it answers: Does the pipeline keep recoverable and irrecoverable uncertainty distinct and visible from source through synthesis?
- Required real runtime path: Process at least one low-confidence extraction, one ambiguous span or page boundary, and one irrecoverable defect such as cropped or unreadable content through all relevant stages.
- Evidence that must be inspectable or saved: Stage-level uncertainty records, final artifact markers showing unresolved versus missing content, and provenance fields preserving confidence and transformation type.
- What does not count as proof: A generic warning banner, a single undifferentiated confidence score, or silent omission of damaged regions.

- Probe name: Artifact independence under shared evidence
- Question it answers: Are the two artifacts independently synthesized from shared evidence rather than one being a reformatted derivative of the other?
- Required real runtime path: Full pipeline execution through all four stages with separate synthesis rules for the two artifact types.
- Evidence that must be inspectable or saved: Both final artifacts from one run, stage evidence showing shared upstream inputs, and synthesis evidence showing that canonical reconstruction did not inherit semantic normalization from highlight processing.
- What does not count as proof: Splitting one output after generation, generating one artifact from the other, or relying on downstream tooling assumptions to justify artifact structure.

## Admissibility Inputs For Harness Work

When the harness needs a strict admissibility report, derive it from this file and the rest of `harness/project-spec/**` by naming:

- Invariant constraints: Preserve two independent artifact outputs, typed provenance, visible uncertainty taxonomy, source authority, stage-specific truth claims, canonical non-normalization by default, and the prohibition on semantic overwrite of uncertain reconstruction.
- Task constraints: Current work may refine implementation, schemas, tests, or inspectability only within the invariant space defined here and in the project spec. It may not silently expand interpretive authority or weaken auditability.
- Constraint conflicts: Stop when readability improvements threaten canonical fidelity, when context expansion drifts toward semantic inference, when provider convenience threatens provenance locality or inspectability, or when downstream consumer pressure attempts to redefine artifact truth claims.
- Allowed transformation types: Extraction improvements, structural inference improvements, annotation-form classification refinement, schema-preserving formatting changes, inspectability improvements, confidence calibration updates, and documentation or tests that clarify the existing invariant space.
- Affected surfaces: `harness/project-spec/**`, active plans and trackers, future pipeline code for extraction, reconstruction, annotation interpretation, artifact synthesis, verification harnesses, and artifact schemas.
- Non-affected surfaces: Auth systems, remote deployment architecture, downstream integrations, storage backends, and compatibility layers unless separately approved.
- Admissibility checks: Confirm that the change preserves artifact independence, preserves or improves provenance typing, keeps uncertainty visible, stays within the interpretive authority boundary, preserves stage inspectability, and does not introduce unauthorized normalization or silent repair.
- Stop conditions: Stop and escalate if a proposed change requires project-spec amendment, introduces external service or storage commitments, deletes or obscures source-linked evidence, blends the artifacts, or cannot explain how lineage and uncertainty remain inspectable after the change.
