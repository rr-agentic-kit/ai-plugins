# fix

Function-style executor for `--fix-broken-tests`, `--refactor-tests`, `--reduce-duplication`.

## Input

`PhaseInput` with `phase: "fix"`.

Required:
- `payload.scope` (typically failing test paths or diff)
- Failure context from user prompt or CI logs when provided

## Execution

1. Reproduce failures with project test command.
2. Apply minimal fixes per intent:
   - `fix-broken`: restore green suite
   - `refactor`: improve structure without behavior change
   - `reduce-duplication`: dedupe per [shared-heuristics.md](../../skills/rr-builder/rr-tester/refs/shared-heuristics.md) redundancy signals
3. Rerun implicated tests; populate `rerun`.
4. Document `risk_notes` for non-obvious changes.

Verify gate: [determinism.md](../../skills/rr-builder/rr-tester/refs/determinism.md).

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-builder/rr-tester/refs/contracts.md) § fix.

## Constraints

- No assess verdict (optional follow-up assess is skill-owned).
- No migration across frameworks (use migrate agent).
