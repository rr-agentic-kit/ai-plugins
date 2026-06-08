# plan

Function-style executor for `--plan-test-strategy`, `--design-test-architecture`, `--define-testing-pyramid`, and plan step in complete-missing chain.

## Input

`PhaseInput` with `phase: "plan"`.

Required:
- `prior_outputs.identify-missing` for gap-closure chains
- `prior_outputs.assess` when available (calibration / overtest findings)
- `payload.scope`, `payload.target`
- Optional constraints from user prompt

## Execution

1. **Trim-before-add:** When assess reports `overtest_tests[]`, weak multi-behavior tests, or high `counts.overtest`:
   - Prioritize `maintain` steps that trim assertions, split multi-behavior tests, or remove implementation coupling **before** `add` steps for new coverage.
   - Rationale must cite assess signal or `overtest_tests[]` entry.
2. Split work into `maintain` (strengthen or trim existing) and `add` (new tests) tracks.
3. Apply **Google S/M/L** sizing from [shared-heuristics.md](../../skills/rr-test/refs/shared-heuristics.md):
   - Prefer S/M tests with right-calibrated assertions over single L test with full-object equality.
   - L flows → split into S/M steps in plan when feasible.
4. Each step: `id`, `action`, `path`, `priority`, `rationale`.
5. Apply merge/sort rules from [determinism.md](../../skills/rr-test/refs/determinism.md).
6. Record `constraints_applied` (epoch budget, target, pyramid stance, trim-before-add when triggered).

Architecture/pyramid flags widen rationale scope but share the same output schema.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § plan.

## Constraints

- No file edits.
- Do not run tests.
