# assess

Function-style executor for `--assess` and `--identify-redundant-tests`. No plan/write decisions.

## Input

`PhaseInput` with `phase: "assess"`.

Required context:
- `payload.scope`, `payload.target`
- Load [shared-heuristics.md](../../skills/s-tester/refs/shared-heuristics.md) for verdict, calibration, redundancy, overtest, exhaustive enumeration, and **Production fidelity and predicate isolation**
- Load [coverage-exclusions.md](../../skills/s-tester/refs/coverage-exclusions.md) for non-testable taxonomy
- Apply scope ordering from [determinism.md](../../skills/s-tester/refs/determinism.md)
- When brief or production surface includes extract/install/package/refuse/replace/env-detection gates: in **one parallel Read turn**, also load the in-scope CI artifact builder (if present) together with extract/install tests under review — do not Write assess output before that batch completes

## Execution

1. Resolve `target: auto` from detected stack (frontend/backend/devops/scripts).
2. Build `scope_manifest` from expanded scope list (determinism ordering):
   - Populate `production_files` and `test_files` with every file in normalized scope.
   - `unassessed` must be empty when scoring completes.
3. Score **every** manifest entry — bidirectional scoring per scope path:
   - **Under-calibration:** weak assertion patterns, `mutation_gap`, missing error paths → `signals` with kinds `weak_assertion`, `mutation_gap`, `missing_coverage`
   - **Over-calibration:** overtest signals, implementation coupling, multi-behavior → `signals` with kinds `over_assertion`, `implementation_coupling`, `multi_behavior`; populate matching `overtest_tests[]` entries
   - **Maintainability:** mystery guest, unclear intent → `maintainability`, `multi_behavior`
   - **AI artifacts:** placeholder tests, hallucinated APIs, spec drift → `ai_artifact` (high severity)
   - **Redundancy:** when redundancy signals apply → `redundant_tests[]` and `signals` with kind `redundancy`
   - **Test smells:** set optional `smell_id` when mapping to testsmells.org (e.g. `SensitiveEquality` for deep-equal DTO)
   - **Classify non-testable first:** per coverage-exclusions taxonomy → `non_testable` signal with `non_testable_reason` in evidence (do not emit `missing_test`)
   - **Missing test:** testable production file with no paired test → `missing_test` signal (required per shared-heuristics § Exhaustive enumeration)
   - **Fidelity / isolation** (when acceptance signals or production surface include extract, install, package, refuse, replace, or shared env-detection helpers) — apply shared-heuristics § Production fidelity and predicate isolation:
     - Soft extract fixture ≠ in-scope CI artifact builder → `missing_coverage`
     - Refusal via composite classifier without isolated predicate / exact reason → `weak_assertion` or `mutation_gap`
     - Writability/replace strategy or shared-helper subset untested → `missing_coverage`
     - **Stop-rule:** do not assign scope `pass` for those gates when any probe fails
4. Assign scope `verdict`: worst of signal severities and gap risk per shared-heuristics; widespread high-severity `over_assertion` or `ai_artifact` prevents scope `pass`; fidelity/isolation failures on acceptance-signal gates also prevent scope `pass`.
5. For `identify-redundant` action, emphasize `redundant_tests[]`; still emit full assess schema including `overtest_tests[]`.
6. Set `counts.overtest` = length of `overtest_tests[]`; aggregate `counts.pass` / `warn` / `fail` / `redundant` per scope verdicts.
7. Aggregate overall verdict per shared-heuristics (worst child wins).
8. Set `enumeration_complete: true` only when `scope_manifest.unassessed` is empty; otherwise `enumeration_complete: false`.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/s-tester/refs/contracts.md) § assess.

Required fields: `enumeration_complete`, `scope_manifest`, `verdict`, `scopes`, `counts` (including `overtest`), `redundant_tests`, `overtest_tests`.

Each `signals[]` entry must use standardized `kind` from shared-heuristics enum; include `evidence` with concrete pattern (e.g. "12-field deep-equal on OrderDTO"); `smell_id` when applicable.

| `status` | When |
|----------|------|
| `ok` | All manifest entries scored; `enumeration_complete: true` |
| `partial` | `scope_manifest.unassessed.length > 0` |
| `failed` | Cannot enumerate scope (e.g. scope expansion error) |

## Constraints

- Read-only: no test file edits.
- Do not emit plan steps or write instructions.
- Do not stop after N findings; emit all signals in scope.
