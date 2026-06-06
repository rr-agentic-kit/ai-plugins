# plan

Function-style executor for `--plan-test-strategy`, `--design-test-architecture`, `--define-testing-pyramid`, and plan step in complete-missing chain.

## Input

`PhaseInput` with `phase: "plan"`.

Required:
- `prior_outputs.identify-missing` for gap-closure chains
- `payload.scope`, `payload.target`
- Optional constraints from user prompt

## Execution

1. Split work into `maintain` (strengthen existing) and `add` (new tests) tracks.
2. Each step: `id`, `action`, `path`, `priority`, `rationale`.
3. Apply merge/sort rules from [determinism.md](../../skills/rr-test/refs/determinism.md).
4. Record `constraints_applied` (epoch budget, target, pyramid stance).

Architecture/pyramid flags widen rationale scope but share the same output schema.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § plan.

## Constraints

- No file edits.
- Do not run tests.
