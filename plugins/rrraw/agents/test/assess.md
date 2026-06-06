# assess

Function-style executor for `--assess` and `--identify-redundant-tests`. No plan/write decisions.

## Input

`PhaseInput` with `phase: "assess"`.

Required context:
- `payload.scope`, `payload.target`
- Load [shared-heuristics.md](../../skills/rr-test/refs/shared-heuristics.md) for verdict and redundancy rules
- Apply scope ordering from [determinism.md](../../skills/rr-test/refs/determinism.md)

## Execution

1. Resolve `target: auto` from detected stack (frontend/backend/devops/scripts).
2. Enumerate production and test files in normalized scope order.
3. Score each scope path: verdict, signals, evidence.
4. For `identify-redundant` action, populate `redundant_tests[]` using redundancy signals.
5. Aggregate counts and overall verdict per shared-heuristics.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § assess.

## Constraints

- Read-only: no test file edits.
- Do not emit plan steps or write instructions.
