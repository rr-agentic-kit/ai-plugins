---
name: context-engineer-create
description: Create one agent context artifact from a template with static, pre-write reflection, and pre-ship gates.
---

# Create

## Input contract

**REQUIRED:** one-line goal; artifact type (or classify first via `/context-engineer`); target path inside the plugin tree.

## Execution

### Progress

Before any other step:

1. Execute **Action: create** in skill **context-engineer** (follow skill **Run:** to load the internal procedure).
2. Call **TodoWrite** with `merge: false` and one todo per step (`create-1-classify` … `create-4-gates`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Do not skip pre-write reflection or pre-ship. On `PRE-WRITE REFLECTION FAILED` or `PRE-SHIP FAILED`, do not write the file.

## Output

- Path written (on success) or failed reflection/pre-ship tables (on failure).
- Pre-write reflection summary (PASSED or FAILED).
- One-line why each change was necessary.
