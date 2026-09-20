# Slice pipeline (builder orchestration)

**Audience:** `rr-builder` in **orchestrate** mode (drive/scope flags or no lane flag). SoT for lifecycle, task-step stage contracts, cursor, and drive×scope run loop. Handoff mode does **not** advance this pipeline beyond the explicit nested skill. Handoff load table: [routing.md](routing.md).

## Slice lifecycle

```
slice ready
  → task-list                    # rr-prepare L1
    → [ per task:
          task detail              # rr-prepare L2 (+ steps breakdown)
          → [ per task-step:
                plan → build → review → refactor(TBD) → step-validate
                  → [ ship? ]      # if plan Ship.ship_after = step_validate
              ]
          → task-validate
          → [ ship? ]              # if a step’s Ship.ship_after = task_validate
        ]
  → slice validate
  → slice delivered              # residual ship boundary → rr-ci when nothing shipped mid-slice
```

Prepare phases (task-list, task detail) remain **rr-prepare**. Orchestrate routes there when the cursor is still in prep (no detailed buildable work yet).

## Task-step stage contracts

| Stage | What builder does | Loads | Executes code? | Done-when |
|-------|-------------------|-------|----------------|-----------|
| **plan** | Ensure feature branch ([feature-branch.md](feature-branch.md)), then produce/enrich step plan + assessment only | [plan-knowledge.md](plan-knowledge.md) allowlist (includes feature-branch) | **No** app source (git branch create/checkout OK) | Branch settled + sidecar `{NNNN}-{step}.plan.md` complete per [plan-schema.md](plan-schema.md) (incl. **Ship**); set `step_plan_done: true` |
| **build** | Implement the step | Current `{NNNN}-{step}.plan.md` + minimal task Goal/Obligations if needed; full **rr-coder** + **rr-tester** (code **and** tests for the step). **Do not** Read other steps’ `.plan.md` files or inlined plan prose from the task body | **Yes** | Code + tests for the step land; step verify checks runnable; set `step_build_done: true` |
| **review** | Full multi-lane review with fix | **rr-review** with **`--fix --all`** (forced) | Via review fix path | Review run complete; fix applied per review; set `step_review_done: true` |
| **refactor** | **TBD** | — | — | Stub: **skip** or stop with `refactor stage not specified` — do **not** invent procedure |
| **step-validate** / **task-validate** | Rubric: Goal / Verify for step scope or full task | [task-validate.md](task-validate.md) | No (assessment) | PASS/FAIL; then maybe **ship** per plan Ship |
| **ship** | Resolve branch/base; hand off **rr-ci** | [ship.md](ship.md) then `skills/rr-ci/SKILL.md` | Via rr-ci only | [ship.md](ship.md) done-when; set `step_ship_done: true` when step-scoped |
| **slice validate** | Rubric: did **slice** hit slice goal / AC | [slice-validate.md](slice-validate.md) | No (assessment) | PASS/FAIL against execute-slice / pinned AC |

### Knowledge load vs full-skill handoff

| Stage / mode | Behavior |
|--------------|----------|
| **plan** (orchestrate) | **Read** only [plan-knowledge.md](plan-knowledge.md). Run [feature-branch.md](feature-branch.md) ensure **first**. Emit plan per [plan-schema.md](plan-schema.md) to `{NNNN}-{step}.plan.md`. Do **not** run rr-coder/rr-tester implement procedures. |
| **build** (orchestrate) | **Read** current step plan `{NNNN}-{step}.plan.md` (read-budget: this file only among plans), optional thin task Goal/Obligations, then nested `rr-coder/SKILL.md` and `rr-tester/SKILL.md` and follow them for the step (code + tests). |
| **review** (orchestrate) | **Read** `rr-review/SKILL.md`; force `--fix --all` regardless of user omission. |
| **ship** (orchestrate) | **Read** [ship.md](ship.md), then `skills/rr-ci/SKILL.md`. Do **not** invent forge CLI in builder. |
| Explicit lane flag | Full-skill **handoff** — see [routing.md](routing.md). No pipeline advance past that skill’s done-when. |

## Cursor persistence (minimal v1)

Prefer extending existing prepare artifacts — no third parallel state file.

| Field | Where | Values / notes |
|-------|--------|----------------|
| `builder_stage` | `{NNNN}.md` frontmatter (active task) and/or `task-summary.md` | `prepare` \| `plan` \| `build` \| `review` \| `refactor` \| `step_validate` \| `ship` \| `task_validate` \| `slice_validate` \| `delivered` |
| `step_index` | `{NNNN}.md` frontmatter | 0-based index into that task’s **Steps** (omit when stage is prepare / task_validate / slice_validate / delivered) |
| `step_plan_done` | `{NNNN}.md` frontmatter | `true` \| `false` — applies to current `step_index`; reset to `false` when advancing `step_index` |
| `step_build_done` | `{NNNN}.md` frontmatter | `true` \| `false` — same scope as `step_plan_done` |
| `step_review_done` | `{NNNN}.md` frontmatter | `true` \| `false` — same scope as `step_plan_done` |
| `step_ship_done` | `{NNNN}.md` frontmatter | `true` \| `false` — step-scoped ship; treat as `true` when plan `ship_after: never` (nothing to ship). Reset when advancing `step_index` |
| `active_ship_branch` | `task-summary.md` | Last resolved ship head branch (from plan Ship / feature-branch) |
| `ship_base_branch` | `task-summary.md` | Last resolved PR/MR base (`default` branch name or prior open tip) |
| `prepare_status` | `task-summary.md` | Existing: `l1` \| `l2` \| `complete` — still authoritative for prep completeness |

Update fields when a stage’s done-when passes — **before** looping or stopping. Do not invent a second cursor store. Do **not** infer plan/build/review/ship completion from prose alone — use the booleans (+ Ship section for whether ship applies).

## Cursor algorithm

Probe order — **first match wins** (this is the **next** stage for `scope: next`, and the head of the remaining path for `scope: full`). Read only frontmatter fields above + current step plan **Ship** when noted — do **not** invent completion from scanning step markdown narrative.

1. **No pin-complete kernel / no `slice_id`** → stop or AskQuestion (need plan freeze / path).
2. **Missing / incomplete prepare** (`outlined` rows, or `prepare_status` ≠ `complete`) → stage **prepare** → load **rr-prepare**.
3. **Active task** has next **task-step** with `step_plan_done` ≠ `true` → **plan**.
4. **`step_plan_done: true` and `step_build_done` ≠ `true`** → **build**.
5. **`step_build_done: true` and `step_review_done` ≠ `true`** → **review** (`--fix --all`).
6. **`step_review_done: true`** → **refactor** stub (skip until specified) → **step-validate** (until PASS/FAIL recorded for this step).
7. **After step-validate PASS** — Read plan Ship for this step:
   - `ship_after: step_validate` and `step_ship_done` ≠ `true` → **ship**.
   - else → treat `step_ship_done` as satisfied for advance; go to 8.
8. **Advance** — If more steps remain: next `step_index`, set `step_plan_done` / `step_build_done` / `step_review_done` / `step_ship_done` to `false`. If no more steps → **task-validate**.
9. **After task-validate PASS** — If any step plan in this task has `ship_after: task_validate` and that ship not yet done → **ship** (use that step’s Ship block; if several, AskQuestion once). Else → next task or step 10.
10. **All tasks validated** → **slice validate**.
11. **Slice validate PASS** → stop: **slice delivered** → point engineer to **rr-ci** only for residual unshipped work (do **not** open PR from builder). Mid-slice ships already handed off via **ship**.

Explicit lane flag wins over this cursor even if `builder_stage` says otherwise ([input-resolution.md](input-resolution.md)).

## Readiness set (`drive: manual`, `scope: full`)

From the cursor algorithm over **remaining** stages until **delivered**:

| Class | Rule |
|-------|------|
| **ready** | Stage whose prior done-when is met (no open prereq) — runnable now |
| **blocked** | Stage whose prior done-when is unmet — list with prereq for guidance; **not** offered as runnable |
| **`(next)`** | Suffix on the ready item that the cursor algorithm would pick under `scope: next` — exactly one label when a next stage exists |

Linear pipeline usually yields **one** ready stage (that item is also **`(next)`**). Still list the remaining blocked path. AskQuestion **only** among the ready set — never offer blocked stages as executable choices. When presenting the ready list (AskQuestion options or prose), mark that cursor stage as e.g. `build (next)` so the engineer sees which choice `--next` would have run.

## Orchestrate run loop (drive × scope)

Resolve `payload.drive` / `payload.scope` defaults in [input-resolution.md](input-resolution.md). Then:

```
resolve flags + cursor
  → probe cursor / readiness set
  → decide drive × scope:
       auto × next  → execute next stage → stop at done-when
       auto × full  → execute next stage → if not delivered and not hard stop → re-probe → repeat
       manual × next → show next stage (AskQuestion confirm/edit) → execute that one → stop (or wait if user continues)
       manual × full → show ready vs blocked (cursor stage marked (next)) → AskQuestion among ready → execute chosen → re-list until decline / delivered / hard stop
```

| Cell | Behavior |
|------|----------|
| **auto × next** | Run cursor-next stage (may load multiple nested skills/refs **in order** within that stage’s done-when). Persist cursor. **Stop** — do not chain. |
| **auto × full** | Same execute as next, then **loop**: re-probe → next stage until **delivered** or hard stop (validate FAIL, missing kernel, refactor stop, user cancel). Silent chaining requires `drive: auto`. |
| **manual × next** | Present only the next logical stage; wait for confirm/change; execute that one; then wait again or stop if user declines. **Never** execute without confirm. |
| **manual × full** | List remaining stages as **ready** vs **blocked** (+ prereq); mark the cursor stage **`(next)`**; AskQuestion among **ready** only; execute chosen; re-list. **Never** offer blocked as runnable. |

**Hard stop** ends any loop: stage failure, validate FAIL, missing inputs, conflicting flags, user decline. Persist `builder_stage` / `step_index` / `step_*_done` after each successful done-when before the next probe.

**Handoff:** skip this loop — [routing.md](routing.md) handoff table; stop at nested done-when. Drive/scope do not mutate handoff lanes.
