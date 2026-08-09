# plan

Function-style executor for `--plan-test-strategy`, `--design-test-architecture`, `--define-testing-pyramid`, and plan step in complete-missing chain.

## Input

`PhaseInput` with `phase: "plan"`.

Required:
- `prior_outputs.identify-missing` for gap-closure chains
- `prior_outputs.assess` when available (calibration / overtest findings)
- `payload.scope`, `payload.target`
- Optional constraints from user prompt
- Load [coverage-exclusions.md](../../skills/rr-test/refs/coverage-exclusions.md) for `exclude[].tooling`

## Execution

1. **Mandatory maintain steps:** When assess has any `overtest_tests[]`, `redundant_tests[]`, or `maintainability` / `multi_behavior` signals → create one `maintain` step per finding (1:1 mapping).
2. **Trim-before-add:** All `maintain` / `trim` / `redundant` work must complete before any `add` step runs in the same epoch:
   - Prioritize `maintain` steps that trim assertions, split multi-behavior tests, or remove implementation coupling **before** `add` steps for new coverage.
   - Rationale must cite assess signal or `overtest_tests[]` entry.
   - Set `maintain_before_exclude_before_add: true` in complete-missing chains.
   - `exclude` track from `excluded[]`; one `coverage_exclude` step per entry.
   - `add` track empty until maintain and exclude queues cleared or user `wontfix` in `constraints_applied` (source: `user`).
3. Split work into `maintain` (strengthen or trim existing), `exclude` (coverage exclusion), and `add` (new tests) tracks.
4. Apply **Google S/M/L** sizing from [shared-heuristics.md](../../skills/rr-test/refs/shared-heuristics.md):
   - Prefer S/M tests with right-calibrated assertions over single L test with full-object equality.
   - L flows → split into S/M steps in plan when feasible.
5. Each step: `id`, `action`, `path`, `priority`, `rationale`.
6. Apply merge/sort rules from [determinism.md](../../skills/rr-test/refs/determinism.md).
7. Set `steps_total` = `maintain.length + exclude.length + add.length`.
8. Set `maintain_before_exclude_before_add: true` in complete-missing chains.
9. Record `constraints_applied` (epoch budget, target, pyramid stance, trim-before-add when triggered).

Architecture/pyramid flags widen rationale scope but share the same output schema.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § plan.

Required fields: `maintain`, `exclude`, `add`, `constraints_applied`, `steps_total`, `maintain_before_exclude_before_add`.

## Constraints

- No file edits.
- Do not run tests.
- Do not defer maintain steps to a later epoch unless prior epoch completed all maintain steps.
