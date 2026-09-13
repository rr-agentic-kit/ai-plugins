# flaky

Function-style executor for `--diagnose-flaky`.

## Input

`PhaseInput` with `phase: "flaky"`.

Required:
- `payload.scope` pointing at flaky test(s)
- Symptom data: failure logs, rerun pattern, CI metadata when available

Load severity categories from [shared-heuristics.md](../../skills/rr-builder/rr-tester/refs/shared-heuristics.md).

## Execution

1. Classify flake pattern (timing, order, shared state, env, concurrency).
2. Assign `severity`.
3. Propose `stabilization_actions` sorted by priority.
4. Recommend quarantine only when severity is `critical` or CI blocker.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-builder/rr-tester/refs/contracts.md) § flaky.

## Constraints

- Diagnosis and recommendations only unless user explicitly requests fix in same session.
- No epoch or chain logic.
