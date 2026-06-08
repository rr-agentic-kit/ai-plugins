# assess

Function-style executor for `--assess` and `--identify-redundant-tests`. No plan/write decisions.

## Input

`PhaseInput` with `phase: "assess"`.

Required context:
- `payload.scope`, `payload.target`
- Load [shared-heuristics.md](../../skills/rr-test/refs/shared-heuristics.md) for verdict, calibration, redundancy, and overtest rules
- Apply scope ordering from [determinism.md](../../skills/rr-test/refs/determinism.md)

## Execution

1. Resolve `target: auto` from detected stack (frontend/backend/devops/scripts).
2. Enumerate production and test files in normalized scope order.
3. **Bidirectional scoring** per scope path:
   - **Under-calibration:** weak assertion patterns, `mutation_gap`, missing error paths → `signals` with kinds `weak_assertion`, `mutation_gap`, `missing_coverage`
   - **Over-calibration:** overtest signals, implementation coupling, multi-behavior → `signals` with kinds `over_assertion`, `implementation_coupling`, `multi_behavior`; populate matching `overtest_tests[]` entries
   - **Maintainability:** mystery guest, unclear intent → `maintainability`, `multi_behavior`
   - **AI artifacts:** placeholder tests, hallucinated APIs, spec drift → `ai_artifact` (high severity)
   - **Redundancy:** when redundancy signals apply → `redundant_tests[]` and `signals` with kind `redundancy`
   - **Test smells:** set optional `smell_id` when mapping to testsmells.org (e.g. `SensitiveEquality` for deep-equal DTO)
4. Assign scope `verdict`: worst of signal severities and gap risk per shared-heuristics; widespread high-severity `over_assertion` or `ai_artifact` prevents scope `pass`.
5. For `identify-redundant` action, emphasize `redundant_tests[]`; still emit full assess schema including `overtest_tests[]`.
6. Set `counts.overtest` = length of `overtest_tests[]`; aggregate `counts.pass` / `warn` / `fail` / `redundant` per scope verdicts.
7. Aggregate overall verdict per shared-heuristics (worst child wins).

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § assess.

Required fields: `verdict`, `scopes`, `counts` (including `overtest`), `redundant_tests`, `overtest_tests`.

Each `signals[]` entry must use standardized `kind` from shared-heuristics enum; include `evidence` with concrete pattern (e.g. "12-field deep-equal on OrderDTO"); `smell_id` when applicable.

## Constraints

- Read-only: no test file edits.
- Do not emit plan steps or write instructions.
