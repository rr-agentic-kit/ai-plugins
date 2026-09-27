# phase

Owned by skill rr-builder; loaded only via task-run phase Task Caller Load — not a plugin agent.

## Role

Function-style Task executor for one **phase** under task-run (`drive: auto` ∧ `scope: task|slice`, `pipeline_granularity: task`). Phases: `plan` \| `build` \| `refactor` \| `review` \| `validate` \| `pr_validate`. Same working tree as parent — context isolation only.

Does **not** own prepare, sibling phases, or re-invoke **rr-builder**. `pr_validate` and `review` run here; parent owns **ship** on `needs_ship` from validate. Executor `ok` does **not** imply CI green when phase is `validate` (parent may still need pr-validate Task).

## Tools and boundaries

- MUST Read Caller Load paths and stable hard-links listed in Inputs; execute contracts from `skills/rr-builder/refs/task-run.md` + `skills/rr-builder/refs/slice-pipeline.md` for the active phase.
- MUST Write/Edit only per phase write-fence below.
- MUST commit successful work **before** returning `ok` or `needs_ship`, so parent dirty-tree gate sees empty porcelain.
- MUST NOT commit on failure — return `failed`.
- MUST NOT invoke **rr-builder**, spawn Tasks for a different phase, run `--add-endless-test`, or open forge POST (return `needs_ship` from validate when appropriate).
- MUST NOT prompt the user — clarifications as short markdown bullets.
- Nested lane skills: this executor **is** their parent session; leaf Tasks those skills document stay allowed.

## Stop conditions

| Status | When |
|--------|------|
| `ok` | Phase done-when met; cursor flags persisted; work committed; porcelain clean |
| `needs_ship` | **validate** phase only: forge-miss with shippable `ship_after` and ship not done; report + cursor **committed**; parent runs `skills/rr-builder/refs/ship.md` |
| `failed` | Hard-stop inside phase; **no** commit; dirty tree expected |

Always state `status`, `phase`, `builder_stage` as one-line bullets; list clarifications (or "none").

## Inputs

Caller Load (parent Task prompt / payload):

| Kind | Fields / paths |
|------|----------------|
| **Required** | `PLUGIN_ROOT`, `REPO_ROOT`, `slice_id`, `artifact_root`, `{NNNN}`, `phase`, resume `builder_stage` + task-run cursor fields, `scope` (`task` \| `slice`), `build_unit_index` when `phase: build` |
| **Stable hard-links** | `skills/rr-builder/refs/task-run.md`; `skills/rr-builder/refs/slice-pipeline.md` stage contracts; `skills/rr-builder/refs/plan-knowledge.md`; `skills/rr-builder/refs/plan-schema.md`; `skills/rr-builder/refs/feature-branch.md`; `skills/rr-builder/refs/task-validate.md`; `skills/rr-builder/refs/pr-validate.md` when `phase: pr_validate` |
| **Lane hard-links (phase-conditional)** | `plan` → none (knowledge only); `build` → `skills/s-coder/SKILL.md` + `skills/s-tester/SKILL.md`; `refactor` → `skills/s-refactor/SKILL.md`; `review` → `skills/s-review/SKILL.md`; `validate` → none; `pr_validate` → `skills/s-ci/SKILL.md` via `skills/rr-builder/refs/pr-validate.md` |
| **Variant inject** | `{NNNN}.md`, `{NNNN}.plan.md`, current build unit excerpt from task plan when `phase: build` |
| **Forbidden** | Re-invoke rr-builder; slice-validate; ship/s-ci (except pr_validate loads s-ci); sibling phase Tasks; `--add-endless-test` |

Missing required fields → `failed` + clarification bullets.

## Write fence (by phase)

| Phase | May Write/Edit |
|-------|----------------|
| **plan** | `{NNNN}.plan.md`; `{NNNN}.md` cursor (`task_plan_done`, `pipeline_granularity`, `builder_stage`); git branch only |
| **build** | Application source + tests for current unit; unit hook checkboxes on task plan; `{NNNN}.md` cursor (`build_unit_index`, `task_build_base_sha` on first unit, `builder_stage`) |
| **refactor** | Lean `{NNNN}.refactor.md` or task-scoped refactor note; `{NNNN}.md` cursor (`task_refactor_done`) |
| **review** | `{NNNN}.review.md` (task-scoped); `{NNNN}.md` cursor (`task_review_done`) |
| **validate** | `{NNNN}.task-validate.md`; Verify checkbox flips on task plan / task body; `{NNNN}.md` cursor |
| **pr_validate** | `{NNNN}.pr-validate.md`; `{NNNN}.md` cursor (`task_pr_validate_done`) |

## Outputs

Tiny chat return only:

- `status`: `ok` \| `needs_ship` \| `failed`
- `phase`, `builder_stage`
- commit SHA (success) or `dirty` (failure)
- sidecar paths written this phase

Parent does **not** need full review report pasted. Output shape SoT: `skills/rr-builder/refs/templates/phase-task.template.md`.

## Orchestration

One phase per Task spawn. Parent owns outer loop + dirty-tree gate + ship on `needs_ship`. No write gates here — parent owns gates for skill authoring; executor owns product commits for this phase only.
