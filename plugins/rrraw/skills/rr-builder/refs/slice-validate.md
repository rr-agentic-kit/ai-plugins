# Slice validate rubric

**Audience:** `rr-builder` orchestration after every task in the slice has **task-validate: PASS**. Assessment only — no application source edits; no PR open.

## Inputs

| Input | Source |
|-------|--------|
| Kernel | Pin-complete `execute-slice.yaml` for `slice_id` |
| Pinned AC / outcome | Kernel + cited Plan AC refs |
| Task tree | `docs/rr/tasks/{slice_id}/task-summary.md` + `{NNNN}.md` |
| Per-task verdicts | Prior [task-validate.md](task-validate.md) PASS rows |

## Rubric

| Check | PASS when | FAIL when |
|-------|-----------|-----------|
| **Slice goal / outcome** | Kernel slice goal / stated outcome is met by the combined task delivery | Goal unmet or only a subset of required outcome |
| **Pinned AC** | Every pinned acceptance criterion has evidence | Any pinned AC missing, deferred without AskQuestion, or contradicted |
| **Task coverage** | Every summary row that is in-scope for Execute has `task-validate: PASS` | Outlined/incomplete tasks remain, or any task-validate FAIL |
| **Prepare complete** | `prepare_status: complete` and PR map present | Prepare incomplete or PR map missing |
| **Non-goals / bounds** | Slice Non-goals / out-of-scope from kernel respected | Out-of-scope work treated as delivery proof |

## Verdict

Emit one line: `slice-validate: PASS | FAIL` plus ≤5 bullets of evidence (cite kernel field / AC id + proof). On **PASS**, set `builder_stage: delivered` and stop — point engineer to **rr-ci** for **residual** unshipped work only (do **not** open PR/MR from builder). Mid-slice / task ships already ran via **ship**. On **FAIL**, leave `builder_stage: slice_validate`.

## Out of scope

- Per-task Goal/Verify detail → [task-validate.md](task-validate.md)
- Planned mid-slice / task forge ship → [ship.md](ship.md) + **rr-ci**
- Re-planning product cascade → **rr-planner**
