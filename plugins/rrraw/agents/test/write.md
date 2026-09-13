# write

Function-style executor for `--write-tests`, `--generate-test-data`, `--write-parameterized-tests`, and write step in chains.

## Input

`PhaseInput` with `phase: "write"`.

Required:
- `payload.write_mode` (`standard` | `test-data` | `parameterized`)
- `prior_outputs.plan` when in chain, or direct scope/goal from payload
- Optional `prior_outputs.assess` for calibration context (avoid repeating over-assertion patterns)
- Load [coverage-exclusions.md](../../skills/rr-builder/rr-tester/refs/coverage-exclusions.md) for exclude track execution

## Execution

1. Execute plan steps in order when `prior_outputs.plan` present:
   - Execution order: all `maintain` → all `exclude` → all `add`.
   - Do not start `exclude` until all `maintain` steps completed or user `wontfix` in plan `constraints_applied`.
   - Do not start `add` until all `exclude` steps completed or user `wontfix`.
   - **Exclude track:** discover configs, update shared exclusion list, sync all configured tooling targets; run coverage verify per coverage-exclusions.md.
   - Record each executed step in `steps_completed[]` with `plan_id` and `track`.
   - Record any skipped step in `steps_skipped[]` with `reason`; skipping without `wontfix` → `status: partial`.
2. Implement plan steps or direct write goal for in-scope paths.
3. Follow repo conventions (from CLAUDE.md section or detected layout).
4. **Minimal-assertion tactics** per [shared-heuristics.md](../../skills/rr-builder/rr-tester/refs/shared-heuristics.md):
   - Assert observable outcomes for the behavior under test; match assertion depth to test role (unit vs integration vs E2E).
   - Avoid full-object deep equality when ≤3 fields define the contract.
   - No private API or internal snapshot assertions unless explicitly required by plan.
   - Split multi-behavior cases into separate tests when writing new code.
5. Run **AI validation pipeline** (populate `validation_pipeline` in output):
   | Stage | Requirement |
   |-------|-------------|
   | `compile` | Project compiles / test sources valid |
   | `run` | Test command green → `execution` |
   | `coverage_verify` | After exclude track: paths absent from coverage report → `coverage_verify` |
   | `oracle` | Behavior-breaking check or mutation-style assertion on critical paths → `oracle_check` |
   | `mutation_spot_check` | If project has mutation tooling, run targeted check; else `skipped: true` with note |
   Pipeline order: compile → run → coverage_verify → oracle → mutation_spot_check. Any stage failure stops later stages.
6. **Oracle failure taxonomy** (record in `oracle_check.failures[]`):
   - `no_behavioral_assertion` — test passes but assertion cannot detect regression
   - `spec_drift` — test asserts outdated contract vs production
   - `ai_hallucination` — references non-existent API
   - `over_coupled` — assertion binds to implementation detail
7. Respect verify gate: [determinism.md](../../skills/rr-builder/rr-tester/refs/determinism.md).

### Oracle tactics (agent-local)

- Prefer behavior-breaking change or mutation-style check on critical assertions.
- If infeasible, document in `oracle_check.failures` with taxonomy code and set `passed: false`.
- Parameterized mode: table-driven cases with distinct behavioral dimensions.
- Test-data mode: factories/fixtures with realistic edge cases, not random strings.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-builder/rr-tester/refs/contracts.md) § write.

Required fields: `changes`, `steps_completed`, `steps_skipped`, `execution`, `coverage_verify`, `oracle_check`, `validation_pipeline`, `write_mode`.

| `status` | When |
|----------|------|
| `ok` | All plan steps executed (or skipped with `wontfix`); tests green; oracle passed; compile+run stages passed |
| `partial` | Plan steps skipped without `wontfix`, or tests green but oracle incomplete or mutation_spot_check skipped only |
| `failed` | Compile/run fail, write error, or oracle failed |

## Constraints

- No routing or epoch decisions.
- Do not cherry-pick plan steps.
