---
name: context-engineer-extract
description: Extract a durable agent context draft from chat or workflow notes with provenance.
---

# Extract

## Input contract

**REQUIRED:** source context (paste or tight summary); artifact type if known.

## Execution

### Progress

Before any other step:

1. Read and execute `refs/actions/extract.md` in skill **context-engineer**.
2. Call **TodoWrite** with `merge: false` and one todo per step (`extract-1-ingest` … `extract-5-output`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Execute **Action: extract** in skill **context-engineer**. Prefer chat output unless the user explicitly approved a write and pre-ship passes.

## Output

- Draft body (or path if user approved write and checks passed).
- Provenance: source, assumptions, open questions.
