---
name: context-engineer
description: Classify and clarify agent context artifact design; outputs the next slash for the user to run.
---

# Design assist

**REQUIRED:** a one-line goal, **or** a path hint, **or** explicit permission to classify from the current chat topic.

Execute **Classify** and **Clarify** in skill **context-engineer** only. Do not perform **Action: audit**, **fix**, **redesign**, **test**, **diff**, **create**, or **extract** in this turn unless the user explicitly chose that verb or requests an **inline write** (see Write branch).

## Output

- Artifact type recommendation (if not already fixed) with one-line rationale.
- Clarify answers still needed (max three bullets), or state “ready for action”.
- End with **Next step (user)** below—user must run **one** slash; do not imply commands chain automatically.
- If fix vs redesign is ambiguous, one **AskQuestion**: “Changing what it does?” → redesign if yes, else fix.

## Write branch

When the user **explicitly requests writing a file** at an approved plugin-relative path this turn:

1. If unclear whether they only wanted `/context-engineer-create`, one **AskQuestion**: “Finish here or run `/context-engineer-create`?”
2. If they insist on finishing here: execute design assist write branch in skill **context-engineer** (follow skill **Design assist** and **Run:** for the internal procedure).
3. Call **TodoWrite** with `merge: false` and one todo per step (`design-1-classify` … `design-4-gates`).
4. Mark each todo `completed` before advancing. Do not skip static, pre-write reflection, or pre-ship.
5. Output includes pre-write reflection summary; on `PRE-WRITE REFLECTION FAILED` or `PRE-SHIP FAILED`, do not write.

Do **not** use the write branch when the user only wanted classify/clarify routing.

## Next step (user)

- New file from template → `/context-engineer-create`
- Notes → draft artifact → `/context-engineer-extract`
- Diagnose one file → `/context-engineer-audit`
- Same intent: wording, typos, audit/test FAILs on current contract → `/context-engineer-fix`
- Change outcome, audience, or capabilities → `/context-engineer-redesign`
- Behavior probes → `/context-engineer-test`
- Compare two files → `/context-engineer-diff`
