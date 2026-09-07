# AGENTS.md

## Project

Normalize reconstructs document structure in raw/browser-extracted book text by aligning it to observable layout in the user's scanned PDF pages.

It is not a general OCR engine and it does not replace source wording.

Primary project relation:

`scan pixels + raw text → layout geometry → approximate alignment → structural reconstruction → derived Markdown`

## Project Authority

This repository contains **project-specific specification and authority only**. Workflow, orchestration, escalation, retry behavior, and general engineering operating instructions are external to this harness and belong to Symphony.

Authoritative project documents:

* `harness/project-spec/PROJECT_SPEC.md` — required behavior, probe contract, MVP boundary, stack, reconstruction rules, and acceptance criteria.
* `harness/project-spec/AUTHORITY.md` — canonical authority hierarchy, source immutability, OCR limits, provenance rules, and stop conditions.
* `harness/project-spec/mvp-implementation-plan.md` — project-specific implementation order and acceptance gates.

These documents have distinct scopes.

`mvp-implementation-plan.md` may not redefine the project specification or authority model.

A contradiction between the specification and authority model is a harness defect; do not resolve it by treating implementation, tests, OCR output, heuristics, or model inference as higher project authority.

Existing implementation does not override the harness.

## Core Authority Split

* scanned page pixels are authoritative for **observable layout**;
* raw/browser-extracted text is authoritative for **lexical wording**, whether its extraction is flattened or preserves physical line breaks;
* OCR text is **non-authoritative** and may be used only as a locating/alignment instrument;
* derived Markdown is a reconstruction artifact, never source authority;
* uncertainty must remain explicit when authorized evidence is insufficient.

Existing raw line breaks may be used as alignment evidence when present, but they do not establish paragraph or block boundaries. Page geometry remains authoritative for observable structure.

## Hard Boundary

Do not improve OCR transcription as a substitute for the project goal.

The project succeeds by recovering topology from page geometry and mapping it onto the canonical raw text.
