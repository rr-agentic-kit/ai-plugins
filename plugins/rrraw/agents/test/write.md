# write

Function-style executor for `--write-tests`, `--generate-test-data`, `--write-parameterized-tests`, and write step in chains.

## Input

`PhaseInput` with `phase: "write"`.

Required:
- `payload.write_mode` (`standard` | `test-data` | `parameterized`)
- `prior_outputs.plan` when in chain, or direct scope/goal from payload

## Execution

1. Implement plan steps or direct write goal for in-scope paths.
2. Follow repo conventions (from CLAUDE.md section or detected layout).
3. Run project test command; capture `execution`.
4. Run oracle validation per agent tactics below.
5. Respect verify gate: [determinism.md](../../skills/rr-test/refs/determinism.md).

### Oracle tactics (agent-local)

- Prefer behavior-breaking change or mutation-style check on critical assertions.
- If infeasible, document in `oracle_check.failures` and set `passed: false`.
- Parameterized mode: table-driven cases with distinct behavioral dimensions.
- Test-data mode: factories/fixtures with realistic edge cases, not random strings.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § write.

| `status` | When |
|----------|------|
| `ok` | Tests green and oracle passed |
| `partial` | Tests green, oracle incomplete |
| `failed` | Tests fail or write error |

## Constraints

- No routing or epoch decisions.
