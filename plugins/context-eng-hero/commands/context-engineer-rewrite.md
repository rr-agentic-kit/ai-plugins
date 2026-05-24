---
name: context-engineer-rewrite
description: Rewrite one agent context definition fixing all audit FAILs with static and pre-ship gates.
---

# Rewrite

## Input contract

**REQUIRED:** plugin-relative path. **Preferred:** prior audit report listing FAIL ids.

## Execution

### Progress

Before any other step:

1. Read and execute `refs/actions/rewrite.md` in skill **context-engineer**.
2. Call **TodoWrite** with `merge: false` and one todo per step (`rewrite-1-read` … `rewrite-6-write`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Execute **Action: rewrite** in skill **context-engineer**. Fix **every** FAIL from the audit (critical, major, minor). Minimal diffs only; stop on `PRE-SHIP FAILED`.

## Output

- Patch summary or path updated; static + pre-ship checklist results; no scope creep.
