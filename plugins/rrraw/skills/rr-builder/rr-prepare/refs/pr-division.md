# L3 PR division

**Audience:** After all L2 tasks are `detailed`. No forge open (**rr-ci** later).

## Heuristics

| Isolate as own PR | Keep in task PR |
|-------------------|-----------------|
| Refactor required to make the real change safe / reviewable | Small local refactor incidental to the change |
| Schema/migration with non-trivial rollback risk | Migration with trivial/no rollback risk |
| Task too long for one reviewable PR → split after detail | Single coherent ship unit |

## Emit

1. Assign `pr_group` on each task frontmatter and on summary rows.
2. Add **PR map** section to `task-summary.md` (group id → task ids → one-line rationale). Optional note: whether the group expects **stacked** mid-slice PRs (`Ship.base: prior_open_pr` on step plans) vs one PR at task/slice end.
3. Do **not** open PR/MR. Do **not** invent concrete `feat/{NNNN}-{step}-…` names here — those land in step plans (`refs/plan-schema.md` **Ship** + `refs/feature-branch.md` under rr-builder).

## Stop

Prepare `complete` after PR map written. Hand off to humans / later orchestrate (**plan** owns branch + `ship_after`) + **rr-ci** on **ship**.
