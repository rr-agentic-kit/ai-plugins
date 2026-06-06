# debug

Function-style executor for `--debug-failing`.

## Input

`PhaseInput` with `phase: "debug"`.

Required:
- Failing test path(s) in `payload.scope`
- Failure logs / stack traces from user or test run

## Execution

1. Parse failure output; classify `diagnosis`:
   - `red`: test exposes real defect
   - `green`: test or fixture defect
   - `inconclusive`: insufficient evidence
2. State `root_cause` with evidence citations.
3. Emit ordered `fix_plan` (investigation steps if inconclusive).

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § debug.

## Constraints

- Does not apply fixes (fix agent) unless user conflates flags — skill routes `fix-broken` separately.
