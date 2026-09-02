# Fix intake (reference)

Used by **Action: fix** step 1. Intake proceeds with stated assumptions per `questioning.md`—these fields are **done-when for apply**, not hard stops at intake.

## Done-when for apply (before `fix-2-plan` completes)

- Plugin-relative **path** to the definition file.
- **Failure source** (one or more):
  - Prior **audit** report with every FAIL id (critical, major, minor), or
  - Prior **test** report with probe FAIL ids tied to the same contract, or
  - User **symptom list** mapped to concrete edits (no scope expansion).

## AskQuestion (when ambiguous)

Use when the user did not supply an audit/test report and intent is unclear:

1. **Preserve primary outcome?** — yes / no / unsure (if no → recommend **redesign**).
2. **Input type** — audit report / test report / symptom list only.
3. **Scope** — fix listed failures only / user proposes extra edits (reject extra unless user re-runs **redesign**).

## Reject

- Outcome or capability change ("add a step", "remove gate", "change audience") → **Action: redesign**, not fix.
- "Critical only" shortcut when an audit report lists minor/major FAILs → fix **every** listed FAIL.

## Mapping rule

Each FAIL id or symptom must map to one concrete edit before step 2 (`fix-2-plan`) completes.

**Eval-first:** Fix only what FAILs require; do not thicken with anticipated rules. Re-run **test** after fix when probes exist.
