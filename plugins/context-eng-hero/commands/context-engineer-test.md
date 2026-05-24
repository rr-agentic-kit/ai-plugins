---
name: context-engineer-test
description: Run fixed behavior probes against one agent context definition (report only).
---

# Test

## Input contract

**REQUIRED:** plugin-relative path to the definition file.

## Execution

### Progress

Before any other step:

1. Read and execute `refs/actions/test.md` in skill **context-engineer**.
2. Call **TodoWrite** with `merge: false` and one todo per step (`test-1-classify` … `test-3-report`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Execute **Action: test** in skill **context-engineer**. No file edits.

## Output

- Probe table with PASS/FAIL/AMBIGUOUS and short notes; regression risks.
