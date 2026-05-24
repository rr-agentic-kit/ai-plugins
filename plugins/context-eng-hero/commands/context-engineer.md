---
name: context-engineer
description: Classify and clarify agent context artifact design; outputs the next slash for the user to run.
---

# Design assist

**REQUIRED:** a one-line goal, **or** a path hint, **or** explicit permission to classify from the current chat topic.

Execute **Classify** and **Clarify** in skill **context-engineer** only. Do not perform **Action: audit**, **rewrite**, **test**, **diff**, **create**, or **extract** in this turn unless the user explicitly chose that verb.

## Output

- Artifact type recommendation (if not already fixed) with one-line rationale.
- Clarify answers still needed (max three bullets), or state “ready for action”.
- End with **Next step (user)** below—user must run **one** slash; do not imply commands chain automatically.

## Next step (user)

- New file from template → `/context-engineer-create`
- Notes → draft artifact → `/context-engineer-extract`
- Diagnose one file → `/context-engineer-audit`
- Minimal edit one file → `/context-engineer-rewrite`
- Behavior probes → `/context-engineer-test`
- Compare two files → `/context-engineer-diff`

**Claude Code:** prefix each with `/context-eng-hero:` (example: `/context-eng-hero:context-engineer-audit`).
