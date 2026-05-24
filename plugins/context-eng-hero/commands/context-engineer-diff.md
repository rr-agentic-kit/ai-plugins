---
name: context-engineer-diff
description: Compare two agent context definitions for intent, contracts, and tradeoffs (report only).
---

# Diff

## Input contract

**REQUIRED:** two plugin-relative paths **A** and **B**.

## Execution

### Progress

Before any other step:

1. Read and execute `refs/actions/diff.md` in skill **context-engineer**.
2. Call **TodoWrite** with `merge: false` and one todo per step (`diff-1-read` … `diff-3-report`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Execute **Action: diff** in skill **context-engineer**. No file edits.

## Output

- Tradeoff summary and recommendation with evidence.
