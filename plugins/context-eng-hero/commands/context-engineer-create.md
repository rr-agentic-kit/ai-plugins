---
name: context-engineer-create
description: Create one agent context artifact from a template with pre-ship validation.
---

# Create

## Input contract

**REQUIRED:** one-line goal; artifact type (or classify first via `/context-engineer`); target path inside the plugin tree.

## Execution

### Progress

Before any other step:

1. Read and execute `refs/actions/create.md` in skill **context-engineer**.
2. Call **TodoWrite** with `merge: false` and one todo per step (`create-1-classify` … `create-5-write`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Execute **Action: create** in skill **context-engineer**. If pre-ship fails, output `PRE-SHIP FAILED` and do not write the file.

## Output

- Path written (on success) or failed checklist table (on failure).
- One-line why each change was necessary.
