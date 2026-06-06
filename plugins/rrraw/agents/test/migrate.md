# migrate

Function-style executor for `--migrate-tests`.

## Input

`PhaseInput` with `phase: "migrate"`.

Required:
- Source framework/runner (from repo or user prompt)
- Target framework/runner (from user prompt or payload details)
- `payload.scope`

## Execution

1. Inventory tests in scope for source patterns.
2. Execute migration steps incrementally; record in `steps_executed`.
3. Note `compatibility_notes` (API gaps, skipped cases).
4. Rerun migrated tests; populate `rerun`.

Verify and reassess gates: [determinism.md](../../skills/rr-test/refs/determinism.md).

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § migrate.

## Constraints

- No routing or assess aggregation (skill chain adds assess).
