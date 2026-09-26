# Learn intake (reference)

Used by **Action: learn** step 1. Intake proceeds with stated assumptions per `questioning.md`—these fields are **done-when for investigate**, not hard stops at intake.

## Done-when for investigate (before `learn-2-investigate` completes)

- **Three path roles** (do not collapse):
  | Role | Meaning | Typical location |
  |------|---------|------------------|
  | **Read-from** | Skill definition to investigate | Plugin **source** preferred; cache/runtime OK **read-only** |
  | **Write-handover** | Where `LEARN-HANDOVER.*` is persisted | **User project** (`docs/rr/LEARN-HANDOVER.<skill>.md` or project root) |
  | **Absorb-into** | Where fix/redesign edits land | **Plugin source** checkout only — never `~/.claude/plugins/cache/**` |
- **Miss source** (one or more):
  - This chat’s **run** (default)—failed steps, human patches, **and/or** friction signals (unnecessary tools/Reads, serial where Ref index co-names peers, invent-vs-procedure, token/interaction waste), or
  - User **problem statement** (seeded description of what went wrong / what they added manually / where the run hurt).

## AskQuestion (when ambiguous)

Use when path or miss is unclear (interactive). Under **`--auto`**, bind with stated defaults when signals present; unresolvable absorb-into still stops.

1. **Target skill?** — paste path / describe location (same pattern as `questioning.md` Missing path). Prefer binding **source** for absorb-into; if user only has cache path, Ask once for source checkout.
2. **Miss overlay?** — use this chat only / add a short problem statement / both.
3. **Failed action id?** — if multiple actions ran; narrow which procedure missed.

## Reject

- No live run and no problem statement → stop; recommend **audit** or **test**, not learn.
- Ambient “improve this skill” with no live run → wrong action.
- User wants a **new** artifact authored from scratch → **create** / **extract**.

## Mapping rule

Miss source must be bound before step 2 (`learn-2-investigate`) completes. Evidence = run behavior or problem statement—do not invent FAILs without that evidence. User may revise topics via **Revise topics** on **post-learn-routing** (interactive) or by editing the written handover.

## Investigate done-when extras (layer-split)

When miss evidence includes founder/human teaching or multi-clause corrections, investigation is incomplete until effort-bar **layer-split** and **mechanism-completeness** in `refs/actions/learn.md` have been applied — outcome reframe alone is not enough.
