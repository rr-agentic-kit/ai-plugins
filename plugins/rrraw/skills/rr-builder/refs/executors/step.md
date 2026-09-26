# step

Owned by skill rr-builder; loaded only via Isolated step run Task Caller Load — not a plugin agent.

## Role

Function-style Task executor for **one task-step** under `drive: auto` ∧ `scope: task|slice`. Runs that step’s inner pipeline `plan → build → refactor → review → step-validate`, resuming from cursor `builder_stage` / `step_*_done`. Same working tree as parent — context isolation only.

Does **not** own prepare, ship/rr-ci, pr-validate, task-validate, slice-validate, or delivered. Does **not** re-invoke **rr-builder**. Executor `ok` does **not** imply CI green — parent runs pr-validate when an open tip was landed.

## Tools and boundaries

- MUST Read Caller Load paths and stable hard-links listed in Inputs; execute stage contracts from `refs/slice-pipeline.md`.
- MUST Write/Edit only: application source + tests for this step; this step’s durable sidecars under `artifact_root` (`{NNNN}-{step}.{plan,refactor,review,validate}.md`); active task `{NNNN}.md` cursor frontmatter (`builder_stage`, `step_index`, `step_*_done`).
- MUST commit successful step work (source + durable sidecars + cursor flags) **before** returning `ok` or `needs_ship`, so parent dirty-tree gate sees empty porcelain.
- MUST NOT commit on failure — leave the tree dirty; return `failed`.
- MUST NOT invoke **rr-builder**, spawn sibling step Tasks, run `--add-endless-test`, open forge POST, or run task-validate / slice-validate.
- MUST NOT prompt the user — clarifications as short markdown bullets.
- Nested lane skills (`rr-coder` / `rr-tester` / `rr-refactor` / `rr-review`): this executor **is** their parent session; leaf Tasks those skills already document stay allowed. MUST NOT invent extra Task fan-out beyond those skills’ own contracts.

## Stop conditions

| Status | When |
|--------|------|
| `ok` | Step-validate done-when met for this step (PASS + forge landing satisfied when shippable, or `ship_after: never`); cursor flags persisted; work committed; porcelain clean. Does **not** imply PR/MR CI green — parent owns [pr-validate.md](../pr-validate.md) |
| `needs_ship` | Step-validate Forge/PR FAIL with `ship_after: step_validate` and ship not done; forge-miss report (+ cursor) written and **committed**; parent must run `refs/ship.md` then re-validate (then pr-validate when tip pushed) |
| `failed` | Hard-stop inside the step (missing inputs, non-forge validate FAIL, review epoch cap, refactor unrecoverable, conflicting state); **no** commit; dirty tree expected |

Always state `status`, `step_index`, `builder_stage` as one-line bullets; list clarifications (or “none”).

## Inputs

Caller Load (parent Task prompt / payload):

| Kind | Fields / paths |
|------|----------------|
| **Required** | `PLUGIN_ROOT`, `REPO_ROOT`, `slice_id`, `artifact_root`, `{NNNN}`, `step_index`, resume `builder_stage` + `step_*_done`, `scope` (`task` \| `slice`) |
| **Stable hard-links** | `refs/slice-pipeline.md` stage contracts; `refs/plan-knowledge.md`; `refs/plan-schema.md`; `refs/feature-branch.md`; `refs/task-validate.md` (step-validate only) |
| **Lane hard-links (resume-conditional)** | Load only pending stages per `step_*_done` (paths under `PLUGIN_ROOT`): plan/build → `skills/rr-builder/rr-coder/SKILL.md` + `skills/rr-builder/rr-tester/SKILL.md`; refactor → `skills/rr-builder/rr-refactor/SKILL.md`; review → `skills/rr-builder/rr-review/SKILL.md`; resuming at step-validate → none |
| **Variant inject** | Current `{NNNN}.md` + `{NNNN}-{step}.plan.md` if present |
| **Forbidden** | Re-invoke rr-builder; slice-validate; task-validate; pr-validate; ship/rr-ci; `--add-endless-test`; parallel sibling steps |

Missing required fields → `failed` + clarification bullets.

## Outputs

Tiny chat return only:

- `status`: `ok` \| `needs_ship` \| `failed`
- `step_index`, `builder_stage`
- commit SHA (success) or `dirty` (failure)
- sidecar paths written this step

Parent does **not** need the full review report pasted. Output shape SoT for the spawn prompt: `refs/templates/step-task.template.md`.

## Orchestration

Sequential stages inside one Task. Parent owns the outer step loop + dirty-tree gate + ship + pr-validate. No write gates here — parent owns gates for skill authoring; executor owns product commits for this step only.
