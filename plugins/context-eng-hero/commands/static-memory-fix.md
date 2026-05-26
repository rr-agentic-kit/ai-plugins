---
name: static-memory-fix
description: Minimal symptom-led fixes to user-global or project CLAUDE.md without full redesign.
---

# Static fix

## Input contract

**REQUIRED:** path to CLAUDE.md; **symptom** (what went wrong—quote bullets or give a short session example).

## Execution

### Progress

Before any other step:

1. Execute **Action: fix** in skill **recipe-static-memory** (follow skill **Run:** to load the internal procedure).
2. Call **TodoWrite** with `merge: false` and one todo per step (`1-fix-read` … `5-fix-write`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

If the user wants a totally different persona or outcome, stop and point to `/static-memory-design`. No scope creep beyond the symptom map.

## Output

- Path
- Sections touched
- Symptom → change mapping
- Patch summary before write; apply only after user confirms
