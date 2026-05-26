---
name: context-engineer-redesign
description: Redesign one agent context definition—with static, pre-write reflection, and pre-ship gates; recommend re-audit after write.
---

# Redesign

## Input contract

**REQUIRED:** plugin-relative path + **delta brief** (outcome/audience/capability/failure-mode changes). Optional: prior diff report between two versions.

## Execution

### Progress

Before any other step:

1. Execute **Action: redesign** in skill **recipe-context-engineer** (follow skill **Run:** to load the internal procedure).
2. Call **TodoWrite** with `merge: false` and one todo per step (`redesign-1-clarify` … `redesign-4-gates`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Structural edits allowed per delta brief; document tradeoffs. Static + pre-write reflection + pre-ship required before write. Do not skip reflection. End with recommendation to run `/context-engineer-audit` on the same path.

## Output

- Patch summary or path updated; impact/tradeoff notes; static + pre-write reflection + pre-ship results; **Next step (user):** `/context-engineer-audit` when behavior or rubric compliance should be verified.
