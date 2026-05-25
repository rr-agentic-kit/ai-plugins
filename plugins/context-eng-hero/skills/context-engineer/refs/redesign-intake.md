# Redesign intake (reference)

Used by **Action: redesign** step 1. Capture deltas before structural planning.

## Required

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

## Stop

Do not treat redesign as “fix all old audit FAILs.” Old FAILs may disappear or new ones may appear—recommend post-write **audit** in output.
