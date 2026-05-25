---
name: your-command-id
description: User-facing purpose in one or two sentences.
---

# <!-- REQUIRED: command heading -->

## Input contract

<!-- REQUIRED: what user/agent must supply -->

## Execution

Execute **Action: …** in skill **<!-- REQUIRED: skill id -->**.

<!-- Do NOT route solely by telling the user to chain other slashes. Use Load + steps in the skill Action, or delegate to a skill Action. -->

## Output

<!-- REQUIRED: shape of response -->

## Validity

Validate against `frontmatter-schemas.md`; before ship run static → `pre-write-reflection.md` → `pre-ship-checklist.md` (see `shared-write-gates.md` in **context-engineer** refs).
