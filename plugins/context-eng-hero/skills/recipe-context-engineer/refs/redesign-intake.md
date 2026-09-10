# Redesign intake (reference)

Used by **Action: redesign** step 1. Intake proceeds with stated assumptions per `questioning.md`—fields below are **done-when for apply**, not hard stops at intake.

## Done-when for apply (before `redesign-2-plan` completes)

- Plugin-relative **path** to the definition file.
- **Delta brief** from the user (paste or bullets): what should change in outcome, audience, capabilities, or failure modes.

## AskQuestion (when fields missing)

1. **Outcome delta** — what should succeed differently?
2. **Audience delta** — who applies this now vs before?
3. **Capabilities** — add / remove / change (enumerate).
4. **Failure modes** — what new bad behavior must be blocked (or removed)?
5. **Breaking change OK?** — yes / no / partial (document tradeoffs in plan).

## Optional

- Two versions to compare → run **diff** first; attach summary to plan.
- Extract draft with **resolved** open questions → first production ship via redesign; polish-only → **fix**.
- Prior **learn handover** when absorb-as implies outcome/audience/capability change → treat approved topics + Incorporate hint as the **delta brief** (same contract as a pasted delta).

## Stop

Do not treat redesign as "fix all old audit FAILs." Old FAILs may disappear or new ones may appear—recommend post-write audit in output. After absorb from learn handover: recommend delete user-project `LEARN-HANDOVER.*` + re-audit/test on **plugin source** (never cache).
