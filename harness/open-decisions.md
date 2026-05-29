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

## Pending Decisions

| ID | Question | Boundary | Needed For | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| PD-001 | Which input substrate does v1 target first: born-digital exports, scanned pages, or mixed-source annotated material? | Scope; architecture | Choosing the first honest vertical slice and extraction approach | Project authority | Pending user choice |
| PD-002 | What is the allowed OCR or vision execution boundary: local-only, remote-allowed, or hybrid opt-in? | Privacy; provider; deployment | Selecting extraction tooling and evidence-locality assumptions | Project authority | Pending user choice |
| PD-003 | What is the first runtime interface: CLI batch pipeline, library-first API, or both? | Interface; implementation shape | Organizing the first implementation seam and validation workflow | Project authority | Pending user choice |
| PD-004 | How should provenance and confidence be encoded inside the markdown artifacts: inline per-entry fields, frontmatter plus section fields, or markdown plus optional sidecar evidence? | Schema; inspectability | Defining artifact schemas and synthesis rules | Project authority | Pending user choice |
| PD-005 | How should confidence be represented in v1: numeric, categorical, or hybrid numeric plus categorical? | Schema; evaluation | Making confidence legible without losing stage-specific meaning | Project authority | Pending user choice |
| PD-006 | What evidence retention policy should apply to stage outputs in early development: full retention, configurable retention, or failure-focused retention? | Storage; observability | Designing inspectability and debugging workflows | Project authority | Pending user choice |
| PD-007 | How broad should the initial annotation taxonomy be: minimal fixed classes, richer controlled vocabulary, or raw-mark plus normalized class? | Schema; interpretation boundary | Implementing annotation interpretation without premature overfitting | Project authority | Pending user choice |
| PD-008 | What reconstruction scope should v1 prove: page-local fidelity, chapter-contiguous reconstruction, or whole-book continuity? | Scope; architecture | Setting reconstruction success criteria and sample size | Project authority | Pending user choice |
| PD-009 | What safe corpus strategy should be used for early probes: public-domain annotated material, private local sample, or a dual-corpus approach? | Data governance; verification | Running acceptance probes without legal or privacy drift | Project authority | Pending user choice |

## Pre-Development Option Matrices

Use these matrices to answer the pending decisions before implementation starts. The recommendation column states the narrowest option that best fits the current spec and governance.

### PD-001 Input Substrate for v1

| Option | Description | What It Buys | Cost / Risk | Effect on First Slice | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | Born-digital annotated exports first | Fastest path to artifact schemas and stage separation with less OCR noise | Under-tests visual extraction and markup ambiguity from real scanned material | Good for proving synthesis and provenance, weaker for proving extraction honesty | Only choose if the immediate goal is schema and pipeline shape rather than full evidence realism |
| B | Scanned annotated pages first | Exercises the hardest evidence problems early and fits the project thesis closely | Higher implementation difficulty and noisier early results | Strongest proof of real-world honesty for extraction, uncertainty, and reconstruction | Recommended if you want the first slice to prove the core UX under realistic conditions |
| C | Mixed-source from day one | Broadest applicability | Expands scope too early and blurs failure analysis | Weakens the ability to isolate stage failures in v1 | Not recommended for first development slice |

### PD-002 OCR / Vision Execution Boundary

| Option | Description | What It Buys | Cost / Risk | Effect on First Slice | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | Local-only processing | Strongest privacy posture and evidence locality; simplest governance story | May limit model quality or increase setup burden | Keeps inspectability and privacy boundaries crisp | Recommended unless you already know remote processing is acceptable |
| B | Remote providers allowed by default | Easier access to stronger OCR / vision services | Adds privacy, deployment, and provider-dependence questions immediately | Accelerates extraction experiments but expands approval-sensitive surfaces | Not recommended before the privacy boundary is explicitly accepted |
| C | Hybrid with remote opt-in | Preserves a local path while allowing comparative evaluation | Adds some complexity in provider abstraction and testing | Good compromise if you need benchmark comparison without making remote the default | Good second choice if comparative benchmarking matters early |

### PD-003 First Runtime Interface

| Option | Description | What It Buys | Cost / Risk | Effect on First Slice | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | CLI batch pipeline first | Cleanest proof path for ingest -> stages -> two terminal markdown artifacts | Less reusable if internal APIs are not separated cleanly | Aligns directly with the current project spec's first interface surface | Recommended |
| B | Library-first API | Easier embedding in future tools and tests | Risks designing abstractions before the runtime truth path is proven | Useful later, but can distract from honest end-to-end evidence | Not recommended as the only first interface |
| C | CLI plus internal library from day one | Gives both external and internal seams | More design overhead up front | Acceptable if kept minimal and the CLI remains the primary proof surface | Acceptable only if the internal API stays subordinate to the CLI proof path |

### PD-004 Provenance / Confidence Encoding in Artifacts

| Option | Description | What It Buys | Cost / Risk | Effect on First Slice | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | Inline per-entry fields inside each markdown artifact | Maximum readability and no hidden dependency on other files | Can become verbose | Best fit for artifact independence and human auditability | Recommended for v1 |
| B | YAML frontmatter plus compact section-level fields | Cleaner body layout for long artifacts | Risks hiding important per-entry distinctions or over-generalizing confidence | Works if the artifact schema remains explicit enough for per-entry audit | Acceptable if paired with explicit per-entry provenance blocks where needed |
| C | Markdown artifacts plus optional sidecar evidence files | Strongest machine-readability for detailed evidence | Can create accidental dependency on sidecars if the markdown becomes too thin | Useful for rich debugging, but the markdown must still stand alone | Good as an optional supplement, not as the primary provenance surface |

### PD-005 Confidence Representation Model

| Option | Description | What It Buys | Cost / Risk | Effect on First Slice | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | Numeric only | Simple for scoring and thresholding | Harder for operators to interpret consistently | Good for later evaluation, weaker for novice legibility | Not ideal alone |
| B | Categorical only | Easy for humans to scan | Loses calibration detail and comparison fidelity | Good for readability, weaker for auditing subtle tradeoffs | Not ideal alone |
| C | Hybrid numeric plus categorical | Keeps machine precision and human legibility | Slight schema overhead | Best match for stage-specific inspectability and novice-safe UX | Recommended |

### PD-006 Stage Evidence Retention Policy

| Option | Description | What It Buys | Cost / Risk | Effect on First Slice | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | Save full stage evidence on every run | Strongest inspectability and easiest debugging | Higher storage use and noisier run outputs | Best for proving honesty during early development | Recommended for early vertical slices |
| B | Configurable retention mode | Balances storage and observability | Requires retention controls earlier | Good long-term posture once the pipeline stabilizes | Good follow-on after the first honest slice |
| C | Failure-focused retention only | Lower storage and simpler output handling | Makes successful runs harder to audit and compare | Weakens the current governance requirement for inspectability | Not recommended for initial development |

### PD-007 Annotation Taxonomy for v1

| Option | Description | What It Buys | Cost / Risk | Effect on First Slice | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | Minimal fixed classes: highlight, underline, fragment, symbol, unknown | Fastest path to real classification | May compress meaningful differences too early | Good for proving the interpretation stage without overscoping | Acceptable minimum |
| B | Rich controlled vocabulary from day one | More descriptive outputs | Higher ontology design burden and more labeling ambiguity | Risks spending time on taxonomy debates before runtime proof | Not recommended for v1 |
| C | Raw visible mark plus normalized class | Preserves observed evidence while still giving normalized outputs | Slightly more schema complexity | Best fit for provenance honesty and later extensibility | Recommended |

### PD-008 Canonical Reconstruction Scope for v1

| Option | Description | What It Buys | Cost / Risk | Effect on First Slice | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | Page-local fidelity only | Smallest scope and easiest iteration | Does not fully prove cross-page continuity | Good for early extraction and formatting checks | Acceptable if you want the absolute smallest first cut |
| B | Chapter-contiguous reconstruction | Proves ordering, hierarchy, and continuity without demanding whole-book scale | More sample preparation and reconstruction logic | Strong balance between ambition and tractability | Recommended |
| C | Whole-book continuity | Most complete fidelity claim | Large blast radius before the pipeline is stable | Too much scope for the first honest slice | Not recommended for first implementation |

### PD-009 Safe Corpus Strategy

| Option | Description | What It Buys | Cost / Risk | Effect on First Slice | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | Public-domain or otherwise reusable annotated material | Simplest reuse and shareability | Hard to find samples with realistic reader markup and edge cases | Good for reproducible verification if such material exists | Good if you already have a suitable corpus |
| B | Private local sample under your control | Highest realism and easiest targeted sample construction | Limits sharing and may constrain collaboration artifacts | Strongest fit for early internal development | Recommended if privacy and local-only processing are acceptable |
| C | Dual corpus: private realism plus public regression sample | Best long-term balance of realism and reproducibility | Requires extra curation effort | Good if you want both private truth-testing and shareable regression checks | Good second-phase choice after an initial sample exists |

## Notes

- Link to archived implementation summaries or decision files when a decision's evidence lives there.
- Do not point active decisions at stale files under `active/` after a bundle has moved to `archive/`.
- Remove decisions that no longer affect current or paused implementation work, or move their final context into the archived bundle summary.
- For rapid user response, answer each pending decision by ID and option letter, for example: `PD-001: B`, `PD-002: A`, `PD-003: A`.
- If a decision remains intentionally deferred, record that explicitly and state the trigger that will force the choice later.
