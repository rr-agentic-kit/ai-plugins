---
name: static-memory-review
description: Walk existing CLAUDE.md section-by-section with accept, edit, or deep-dive gates.
---

# Static review

## Input contract

**REQUIRED:** path to existing CLAUDE.md (user-global or project).

## Execution

### Progress

Before any other step:

1. Execute **Action: review** in skill **recipe-static-memory** (follow skill **Run:** to load the internal procedure).
2. Call **TodoWrite** with `merge: false` and one todo per step (`1-review-read` … `5-review-write`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Per-section **Accept / Edit / Deep-dive** unless the user explicitly batch-approves all sections. Do not write until consolidated changes are approved.

## Output

- Path reviewed
- Sections touched and gate used per section
- Pre-write change summary; disk updates only after approval
