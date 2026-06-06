# identify-missing

Function-style executor for `--identify-missing`. No routing logic.

## Input

`PhaseInput` with `phase: "identify-missing"`.

Required:
- `payload.scope`
- `prior_outputs.assess` when available (else run inline gap scan)

Load [shared-heuristics.md](../../skills/rr-test/refs/shared-heuristics.md) for risk heuristic.

## Execution

1. List production surfaces in scope without adequate test coverage (use assess signals when present).
2. Assign `risk` and `priority` (1 = highest).
3. Suggest `suggested_test_path` following repo conventions from init context or detected layout.
4. Sort items by priority ascending, then production_path lexicographically.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § identify-missing.

## Constraints

- Inventory only; no file writes.
- Do not merge into plan steps (plan agent owns that).
