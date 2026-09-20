# Slice validate rubric

**Audience:** `rr-builder` orchestration after every task in the slice has **task-validate: PASS**. Assessment only — no application source edits; no PR open.

## Persist path (canonical)

`docs/rr/tasks/{slice_id}/slice-validate.md`

Write the report **before** setting `builder_stage: delivered` on PASS.

## Inputs

| Input | Source |
|-------|--------|
| Kernel | Pin-complete `execute-slice.yaml` for `slice_id` |
| Pinned AC / outcome | Kernel + cited Plan AC refs |
| Task tree | `docs/rr/tasks/{slice_id}/task-summary.md` + `{NNNN}.md` |
| Per-task verdicts | Prior [task-validate.md](task-validate.md) PASS rows + `{NNNN}.task-validate.md` reports |

## Validation plan (derive checklist)

Build the report’s **Validation plan** from:

- Kernel slice goal / stated outcome
- Every pinned acceptance criterion (AC ids)
- Every in-scope summary row requiring `task-validate: PASS`
- Prepare completeness (`prepare_status: complete` + PR map)
- Slice Non-goals / out-of-scope bounds from kernel

Do **not** invent criteria absent from kernel / summary / pinned AC.

## Rubric

| Check | PASS when | FAIL when |
|-------|-----------|-----------|
| **Slice goal / outcome** | Kernel slice goal / stated outcome is met by the combined task delivery | Goal unmet or only a subset of required outcome |
| **Pinned AC** | Every pinned acceptance criterion has evidence | Any pinned AC missing, deferred without AskQuestion, or contradicted |
| **Task coverage** | Every summary row that is in-scope for Execute has `task-validate: PASS` | Outlined/incomplete tasks remain, or any task-validate FAIL |
| **Prepare complete** | `prepare_status: complete` and PR map present | Prepare incomplete or PR map missing |
| **Non-goals / bounds** | Slice Non-goals / out-of-scope from kernel respected | Out-of-scope work treated as delivery proof |

## Report body

```markdown
# Slice validate — {slice_id}

## Validation plan
- [ ] <kernel goal / AC / coverage item>
…

## Results

| Item | Verdict | Evidence |
|------|---------|----------|
| <plan item> | PASS \| FAIL | <cite kernel field / AC id + proof> |
…

slice-validate: PASS | FAIL
```

- Per-item column is **PASS** or **FAIL** only.
- Final line must be exactly `slice-validate: PASS | FAIL`.
- Overall **PASS** only when **all** required items PASS.

## Verdict / cursor

Emit chat announce of `docs/rr/tasks/{slice_id}/slice-validate.md`. On **PASS**, set `builder_stage: delivered` and stop — point engineer to **rr-ci** for **residual** unshipped work only (do **not** open PR/MR from builder). Mid-slice / task ships already ran via **ship**. On **FAIL**, leave `builder_stage: slice_validate`.

## Out of scope

- Per-task Goal/Verify detail → [task-validate.md](task-validate.md)
- Planned mid-slice / task forge ship → [ship.md](ship.md) + **rr-ci**
- Re-planning product cascade → **rr-planner**
