# Learn intake (reference)

Used by **Action: learn** step 1. Intake proceeds with stated assumptions per `questioning.md`—these fields are **done-when for investigate**, not hard stops at intake.

## Done-when for investigate (before `learn-2-investigate` completes)

- Plugin-relative **path** to the target skill definition (`SKILL.md` or skill folder).
- **Miss source** (one or more):
  - This chat’s **run** (default)—failed steps, human patches, **and/or** friction signals (excess serial tools/Reads, invent-vs-procedure), or
  - User **problem statement** (seeded description of what went wrong / what they added manually / where the run hurt).

## AskQuestion (when ambiguous)

Use when path or miss is unclear:

1. **Target skill path?** — paste path / describe location (same pattern as `questioning.md` Missing path).
2. **Miss overlay?** — use this chat only / add a short problem statement / both.
3. **Failed action id?** — if multiple actions ran; narrow which procedure missed.

## Reject

- No live run and no problem statement → stop; recommend **audit** or **test**, not learn.
- Ambient “improve this skill” with no live run → wrong action.
- User wants a **new** artifact authored from scratch → **create** / **extract**.

## Mapping rule

Miss source must be bound before step 2 (`learn-2-investigate`) completes. Evidence = run behavior or problem statement—do not invent FAILs without that evidence. User may edit auto-topics later at the approve gate.
