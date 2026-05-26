---
name: static-memory-design
description: Design user-global or project CLAUDE.md from scratch with exhaustive communication and role sections for user scope.
---

# Static design

## Input contract

**REQUIRED:** `scope` — `user` | `project`.

**Optional:** explicit path (default user-global `CLAUDE.md` per Claude Code memory docs; project default `CLAUDE.md` or `.claude/CLAUDE.md` in cwd).

## Execution

### Progress

Before any other step:

1. Execute **Action: design** in skill **recipe-static-memory** (follow skill **Run:** to load the internal procedure).
2. Call **TodoWrite** with `merge: false` and one todo per step (`1-design-scope` … `5-design-write`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Do not write the user’s CLAUDE.md until the action **confirm** step passes. If a meaningful file already exists without rewrite confirmation, stop and recommend review or fix.

## Output

- Path (or planned path) and scope
- Sections drafted
- Confirm-before-write summary; disk path only after user approval in step 5
