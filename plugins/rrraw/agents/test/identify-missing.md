# identify-missing

Function-style executor for `--identify-missing`. No routing logic.

## Input

`PhaseInput` with `phase: "identify-missing"`.

Required:
- `payload.scope`
- `prior_outputs.assess` when available (else run inline gap scan)

Load [shared-heuristics.md](../../skills/rr-test/refs/shared-heuristics.md) for risk heuristic and exhaustive enumeration rules.

## Execution

1. Cross-check assess `scope_manifest.production_files` — every path without adequate coverage must produce an `items[]` entry.
2. Emit an item for every `missing_test` and `missing_coverage` signal from assess (counts must reconcile).
3. Assign `risk` and `priority` (1 = highest).
4. Suggest `suggested_test_path` following repo conventions from init context or detected layout.
5. Populate `uncovered_production_paths` with any production path lacking adequate coverage and without matching `items[]` entry.
6. Set `enumeration_complete: true` only when `uncovered_production_paths` is empty.
7. Sort items by priority ascending, then production_path lexicographically — no truncation.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § identify-missing.

Required fields: `enumeration_complete`, `items`, `summary_counts`, `uncovered_production_paths`.

| `status` | When |
|----------|------|
| `ok` | All production paths covered in `items[]` or adequately tested; `enumeration_complete: true` |
| `partial` | `uncovered_production_paths.length > 0` |
| `failed` | Cannot enumerate scope |

## Constraints

- Inventory only; no file writes.
- Do not merge into plan steps (plan agent owns that).
- Do not truncate item list; emit all gaps in scope.
