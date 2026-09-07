# PROJECT_SPEC.md

# Layout-Guided Markdown Reconstruction — Project Specification

## 1. Purpose

Build a local, deterministic pipeline that reconstructs useful Markdown document structure from:

1. a user-owned scanned PDF, which is authoritative for page geometry and observable layout; and
2. a flat raw/browser-extracted text or Markdown source, which is authoritative for lexical wording unless an explicit repair is authorized.

The system MUST reunite **what the source says** with **where it appears on the page**.

Symphony owns agent runtime/lifecycle. This repository harness MUST define only project goal, scope, contracts, authority, acceptance criteria, and stop conditions. It MUST NOT define agent orchestration, retry policy, model selection, or lifecycle behavior.

---

## 2. Empirical Basis

A proof-of-concept test on an Einstein scan showed:

- Tesseract transcription remained noisy and unsuitable as canonical text.
- Tesseract layout geometry was materially better: paragraph starts were recoverable from stable first-line indentation even when OCR tokens were wrong.
- Approximate alignment between noisy OCR tokens and raw-extracted text is therefore a plausible bridge from page geometry back to the cleaner text stream.

This empirical split is the core project thesis:

> **raw/browser extraction is lexical authority; OCR is a geometry/alignment instrument.**

The first implementation milestone MUST test this thesis across multiple books before any full reconstruction pipeline is built.

---

## 3. Primary Goal

Given a scanned PDF and its corresponding flat extracted text, produce a structure map that can identify, with explicit confidence:

- printed page boundaries;
- physical text lines;
- paragraph starts and continuations;
- headings / section labels where supported;
- running headers;
- page numbers;
- likely captions / footnotes / other page furniture where observable;
- cross-page paragraph continuation;
- source-text spans corresponding to those layout structures.

The system MUST be capable of inserting paragraph/heading boundaries into the flat text without silently rewriting its wording.

---

## 4. Non-Goals

The project MUST NOT, unless this specification is explicitly revised:

- replace raw/browser text with Tesseract transcription;
- optimize Tesseract for book-quality OCR;
- use an LLM to freely rewrite, re-paragraph, summarize, or “clean up” source prose;
- infer exact publisher paragraph boundaries from semantics when page geometry does not support them;
- mutate source Markdown during the probe milestone;
- solve every document-layout class before the probe is proven;
- build a GUI;
- build a retrieval system, vector store, semantic index, or RAG layer;
- implement Symphony lifecycle/runtime behavior inside this repo.

---

## 5. Authority Split

The implementation MUST obey `AUTHORITY.md`.

At a high level:

1. source scan pixels are authoritative for observable layout;
2. raw/browser extraction is authoritative for lexical wording;
3. OCR text is non-authoritative and may be used only to locate/alignment-match geometry;
4. deterministic layout heuristics may classify structure;
5. semantic inference may only resolve explicitly ambiguous cases if later authorized;
6. uncertain structure MUST be represented as uncertain rather than silently invented.

---

## 6. Initial Stack

Target runtime: Python 3.12+.

Initial dependencies:

- `PyMuPDF` — PDF rendering and page access;
- `Pillow` — image operations;
- `pytesseract` — Tesseract TSV/box access;
- Tesseract executable — OCR/layout engine;
- `rapidfuzz` — approximate token/span matching;
- `numpy` — geometry/statistics;
- `opencv-python-headless` — rotation, deskew, gutter/crop helpers where required.

The dependency set MAY be reduced if equivalent behavior is preserved.

PaddleOCR or another OCR engine MUST NOT be added during the first probe merely because Tesseract transcription is inaccurate. A replacement/fallback engine is justified only if Tesseract fails at the geometry task under the probe acceptance criteria.

---

## 7. Architecture Contract

The pipeline is conceptually:

```text
scanned PDF
    ↓
page rendering / orientation / spread splitting
    ↓
positioned OCR tokens + line geometry
    ↓
layout features and candidate structural boundaries
    ↓
approximate alignment to flat raw text
    ↓
source-text span ↔ page-geometry map
    ↓
structure reconstruction
    ↓
Markdown projection
```

### 7.1 Lexical and structural data MUST remain separate

A positioned token record SHOULD resemble:

```json
{
  "ocr_text": "sen5e",
  "page": 12,
  "x0": 322,
  "y0": 544,
  "x1": 413,
  "y1": 573,
  "line_id": 17,
  "ocr_confidence": 82.1
}
```

An alignment record SHOULD map that evidence to the canonical text:

```json
{
  "source_text": "sense",
  "source_start": 1837,
  "source_end": 1842,
  "page": 12,
  "line_id": 17,
  "alignment_confidence": 0.93
}
```

A structural boundary record SHOULD be explicit about evidence:

```json
{
  "kind": "paragraph_start",
  "source_offset": 1924,
  "page": 12,
  "confidence": 0.98,
  "evidence": {
    "first_line_indent_px": 49,
    "median_body_indent_px": 0,
    "vertical_gap_ratio": 1.03
  }
}
```

The exact schema may evolve, but these distinctions MUST remain.

---

## 8. Milestone 0 — Probe

### 8.1 Purpose

Before building a general reconstruction engine, prove or falsify the thesis that Tesseract-derived geometry can recover useful document topology while raw text remains lexical authority.

### 8.2 Probe corpus

Use a small hand-selected sample from at least:

- Einstein — conventional prose / sectioned technical text;
- *Stella Maris* — dialogue-heavy unconventional typography;
- Gärdenfors — numbered hierarchy, figures/captions, headers;
- one additional prose/philosophy source with conventional paragraphs.

Recommended sample: 3–5 representative printed pages per source, including at least one difficult page.

### 8.3 Probe inputs

For each sample:

- source PDF;
- corresponding flat extracted text/Markdown;
- page or spread range to inspect.

### 8.4 Probe outputs

The probe MUST produce all of the following without modifying the source Markdown:

1. **Annotated page image**
   - physical line boxes;
   - inferred paragraph starts;
   - running-header/page-number candidates;
   - confidence markings or labels.

2. **Geometry JSON**
   - page;
   - OCR token boxes;
   - reconstructed physical lines;
   - paragraph-start candidates;
   - relevant measurements.

3. **Alignment report**
   - OCR span;
   - matched raw/source span;
   - alignment confidence;
   - unmatched/ambiguous spans.

4. **Human-readable probe report**
   - detected paragraph starts;
   - confidence;
   - false positives / false negatives found during inspection;
   - any failure mode that would block a full implementation.

The probe MAY additionally emit a non-authoritative preview Markdown, but MUST label it as a preview and MUST NOT overwrite input.

### 8.5 Probe acceptance criteria

The probe passes only if human inspection shows:

- conventional prose paragraph starts are recovered reliably enough to be useful across more than one book;
- OCR transcription errors do not materially prevent alignment for ordinary body text;
- page furniture can be distinguished from body structure often enough to avoid systematic contamination;
- the approach can represent uncertainty instead of forcing a boundary;
- *Stella Maris* yields enough geometric signal to make dialogue-turn reconstruction plausible, or its distinct failure mode is explicitly characterized.

The probe MUST NOT be declared successful based on a single Einstein page.

### 8.6 Probe failure criteria

Stop and reconsider the architecture if any of these are systemic:

- geometry boxes frequently merge unrelated regions;
- line ordering is unstable after orientation/spread preprocessing;
- fuzzy alignment drifts irrecoverably after local OCR errors;
- repeated page furniture causes persistent incorrect text alignment;
- paragraph-start geometry is not stable across representative sources;
- the only way to obtain acceptable output is to trust OCR wording or use unrestricted semantic rewriting.

---

## 9. Geometry Rules

The implementation SHOULD derive structure from measurable geometry, not Tesseract paragraph IDs alone.

Useful features include:

- first-line indentation relative to the dominant body left edge;
- vertical gap relative to local median line spacing;
- line-height change;
- horizontal extent / centeredness;
- repeated text at stable top/bottom positions;
- numbering pattern;
- block isolation;
- cross-page continuation geometry;
- stable page-region recurrence.

Tesseract block/paragraph/line identifiers are signals, not authority.

---

## 10. Page Preprocessing

The implementation MUST make page preprocessing observable and debuggable.

For each rendered source page/spread, preserve enough metadata to explain:

- rotation applied;
- crop applied;
- spread split boundary;
- deskew transformation;
- resulting printed-page order.

Automatic spread splitting MAY be used, but every decision MUST be inspectable.

Manual overrides SHOULD be possible by configuration if automatic gutter detection is wrong.

Preprocessing MUST NOT permanently alter the source PDF.

---

## 11. Alignment Contract

Alignment is between:

- noisy OCR token/line sequences; and
- canonical flat source text.

Requirements:

- approximate, not exact, matching;
- local anchors and bounded windows to prevent global drift;
- explicit unmatched spans;
- resynchronization after page furniture or OCR corruption;
- monotonic source order unless the page-order model explicitly says otherwise;
- repeated phrases MUST NOT be resolved by nearest-string score alone.

The implementation SHOULD prefer many local high-confidence anchors over one global fuzzy match.

Alignment confidence MUST be surfaced.

---

## 12. Structural Reconstruction Rules

### 12.1 Paragraphs

A paragraph boundary MAY be emitted when geometry supports it through one or more strong signals, e.g.:

- first-line indent;
- abnormal inter-line gap;
- isolated paragraph block;
- dialogue-turn spacing;
- page-layout continuation pattern.

Sentence punctuation alone MUST NOT be sufficient evidence of an original paragraph boundary.

### 12.2 Cross-page continuation

A page boundary is not a paragraph boundary by default.

The implementation MUST distinguish:

- paragraph continues onto next printed page;
- new paragraph begins at top of next printed page;
- heading begins at top of next printed page.

### 12.3 Headings

Heading detection MAY use:

- numbering hierarchy;
- typography/line height;
- centeredness;
- isolation;
- repeated section patterns.

Markdown heading *level* is an interpretation and MUST be derived from explicit hierarchy rules, not arbitrary font size alone.

### 12.4 Page furniture

Running headers and page numbers MUST first be classified, not immediately deleted.

The projection layer may omit them from cleaned Markdown once classification confidence is high.

### 12.5 Hyphenation

Line-end hyphenation repair MUST be conservative.

A hyphen MUST NOT be removed merely because a physical line ended with `-`.

Any lexical repair that changes source characters MUST be logged separately from structural edits.

---

## 13. Confidence and Abstention

The system MUST support at least:

- `high`;
- `medium`;
- `low`;
- `unresolved`;

or an equivalent numeric confidence plus thresholds.

Low-confidence structure MUST NOT be silently projected as source fact.

When evidence is insufficient, the correct output is an unresolved candidate requiring review.

---

## 14. Provenance

Every projected structural edit SHOULD be traceable to:

- source text offset/span;
- source PDF page;
- geometry evidence;
- classification rule;
- confidence.

The system MUST preserve the original flat text unchanged.

A reconstructed Markdown file is a derived artifact, never a replacement authority.

---

## 15. CLI Shape

Exact commands may evolve, but the probe SHOULD converge on a simple local interface similar to:

```bash
python -m layout_reconstruct probe \
  --pdf "Einstein.pdf" \
  --text "Einstein.md" \
  --pages 27-31 \
  --out ".probe/einstein"
```

A future reconstruction command MAY resemble:

```bash
python -m layout_reconstruct reconstruct \
  --pdf "Einstein.pdf" \
  --text "Einstein.md" \
  --out "Einstein.reconstructed.md"
```

The final command names are not authoritative; the behavioral contracts are.

---

## 16. Test Strategy

### 16.1 Unit tests

Cover:

- line grouping from token boxes;
- indentation statistics;
- vertical-gap statistics;
- spread ordering;
- page-furniture recurrence;
- fuzzy anchor matching;
- alignment resynchronization;
- confidence calculation;
- cross-page continuation;
- serialization/provenance.

### 16.2 Golden probe fixtures

Maintain small representative fixtures with expected:

- printed-page orientation/order;
- paragraph-start coordinates;
- heading candidates;
- page-furniture classifications;
- source-text alignment anchors.

Golden fixtures SHOULD be small enough to inspect manually.

### 16.3 No metric gaming

A test suite MUST NOT define success solely as token-alignment percentage.

The project goal is correct document structure. A high alignment score with wrong paragraph boundaries is failure.

---

## 17. Development Sequence

Agents SHOULD proceed in this order:

1. repository skeleton and dependency setup;
2. render/orient/split one representative page;
3. extract Tesseract TSV geometry;
4. visualize lines/boxes;
5. infer paragraph-start candidates from geometry;
6. produce probe JSON/report;
7. align geometry to flat text;
8. run probe across the required multi-book corpus;
9. evaluate probe against acceptance criteria;
10. only after probe acceptance, design the generalized reconstruction/projection layer.

Agents MUST NOT skip directly to full-book rewriting.

---

## 18. Explicit Agent Loop Traps and Mitigations

### Trap: “Improve OCR until transcription is clean”
Mitigation: OCR wording is non-authoritative. Optimize geometry/alignment only.

### Trap: Overfit first-line indent to Einstein
Mitigation: probe corpus MUST include dialogue-heavy and hierarchical sources before acceptance.

### Trap: Trust Tesseract `par_num` as truth
Mitigation: derive paragraph evidence from measured geometry; OCR structural IDs are only features.

### Trap: Global fuzzy match drifts after one bad region
Mitigation: local anchors, monotonic windows, page-scoped alignment, explicit resynchronization.

### Trap: Repeated headers poison alignment
Mitigation: classify stable margin recurrence before body-text alignment or exclude those regions from canonical alignment.

### Trap: “Fix” source text while restructuring
Mitigation: source text is immutable during structural projection. Lexical repairs require a separate explicit edit ledger.

### Trap: Turn uncertainty into aggressive heuristics
Mitigation: abstention is required. Unresolved candidates are valid outputs.

### Trap: Build a full framework before proving geometry
Mitigation: Milestone 0 probe is a hard gate.

### Trap: Add more OCR engines prematurely
Mitigation: only replace/add engine if probe evidence shows Tesseract geometry fails.

### Trap: Hide preprocessing mistakes downstream
Mitigation: orientation, crop, gutter split, and deskew outputs MUST be visualizable and logged.

### Trap: Treat page boundaries as paragraph boundaries
Mitigation: explicit cross-page continuation classification and tests.

### Trap: Optimize for pretty Markdown rather than source fidelity
Mitigation: acceptance is based on structural correctness + provenance, not aesthetics.

---

## 19. Definition of Done

### Probe done

Milestone 0 is done when:

- the required multi-book sample has been processed;
- outputs are inspectable;
- paragraph/layout recovery has been manually evaluated;
- failure modes are documented;
- the project thesis is either accepted or falsified with evidence.

### MVP done

The reconstruction MVP is done when:

- a full selected book can be processed end-to-end;
- source text remains unchanged except separately authorized lexical repairs;
- reconstructed paragraphs/headings are materially faithful to page layout;
- page furniture is excluded from cleaned Markdown with provenance;
- uncertainty is surfaced;
- the result is reproducible from the same inputs;
- every structural insertion can be traced back to page/layout evidence.

