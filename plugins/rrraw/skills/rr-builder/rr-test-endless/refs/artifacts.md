# Endless add-test disk artifacts

**Purpose:** Path layout and checkpoint schema for **`rr-test-endless`**. **`REVIEW_DIR/plans/trp-*.md`** is the sole source of truth for work order and execution progress.

## Run id

Mint per **`skills/rr-builder/rr-review/refs/artifacts.md`**: `yyyymmdd-NN` local calendar date + daily counter.

**`REVIEW_DIR`** = `.ai/review/<runId>/`

## Layout

| Path | When written | Contents |
|------|----------------|----------|
| `test/assess/tra-*.md` | Assess `Task` | Per `assess-output.md`; suffix chunk slug when `m > 1` |
| `plans/trp-*.md` | Plan + fix progress | Per `work-pack-sizing.md`; checkbox state on step lines |
| `test/state/endless-add-test-checkpoint.json` | Optional resume | §6.0 checkpoint — never overrides plan files |
| `test/state/*` | Optional telemetry | Never overrides `plans/` |

## Checkpoint JSON (`endless-add-test-checkpoint.json`)

| Field | Type | Meaning |
|-------|------|---------|
| **`version`** | integer | `1` |
| **`iteration_n`** | integer | Outer loop index |
| **`scope`** | string | Normalized **`Scope:`** line |
| **`completed_plan_paths`** | string[] | Worker-success paths for current iteration |
| **`assessment_paths_by_chunk`** | object | `chunk_id` → assess file path (after §1) |
| **`last_verify_head_sha`** | string \| null | Optional post-§7 telemetry |
| **`updated_at`** | string | ISO-8601 |

## Task envelope (fix)

- **`plan_path`**: `trp-*.md` under **`REVIEW_DIR/plans/`**
- **`<base>`**: integration branch — never `master` or `main`
- **`branch_name`**: YAML `branch:` from plan frontmatter

Execution rules → `orchestration.md` §4–§6.
