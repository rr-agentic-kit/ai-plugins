---
name: context-engineer-fix
description: Fix one agent context definition to match existing intent—with static, pre-write reflection, and pre-ship gates.
---

# Fix

## Input contract

**REQUIRED:** plugin-relative path. **Preferred:** prior audit or test report listing FAIL ids. **Alternate:** explicit symptom list tied to concrete edits (no scope expansion).

## Execution

### Progress

Before any other step:

1. Execute **Action: fix** in skill **context-engineer** (follow skill **Run:** to load the internal procedure).
2. Call **TodoWrite** with `merge: false` and one todo per step (`fix-1-read` … `fix-4-gates`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Fix **every** listed FAIL when audit- or test-led (all severities). Minimal diffs only. Do not skip pre-write reflection. Stop on `PRE-WRITE REFLECTION FAILED` or `PRE-SHIP FAILED`. If the user wants to change outcome or capabilities, stop and point to `/context-engineer-redesign`.

## Output

- Patch summary or path updated; static + pre-write reflection + pre-ship results; no scope creep.
