# Slice pipeline (builder orchestration)

**Audience:** `rr-builder` in **orchestrate** or **feature** mode (drive/scope flags, `--feature`, or no lane flag). SoT for lifecycle, task-step stage contracts, cursor, and drive×scope run loop. Handoff mode does **not** advance this pipeline beyond the explicit nested skill. Handoff load table: [routing.md](routing.md). Feature mint + hard stop: [feature.md](feature.md).

## Artifact root (durable paths)

Default (orchestrate on an rr-project slice):

`docs/rr/tasks/{slice_id}/`

When `payload.feature.artifact_root` is set (feature mode / non_rr), resolve **all** durable task/step sidecars under that root instead:

| Kind | Under `artifact_root` |
|------|------------------------|
| Task | `{NNNN}.md` |
| Plan / refactor / review / step-validate | `{NNNN}-{step}.{plan,refactor,review,validate}.md` |
| Task-validate | `{NNNN}.task-validate.md` |
| Summary / registry (rr) | `task-summary.md`, `docs/rr/tasks/registry.yaml` (rr only) |

Scratch stays `.ai/review/<runId>/`, `.ai/refactor/<runId>/` — never relocated under `artifact_root`. Slice-validate / delivered paths apply only to orchestrate `scope: slice` — **feature mode never reaches them**.

Below, paths written as `docs/rr/tasks/{slice_id}/…` mean **`{artifact_root}/…`** when `artifact_root` is set.

## Slice lifecycle

```
slice ready
  → task-list                    # rr-prepare L1
    → [ per task:
          task detail              # rr-prepare L2 (+ steps breakdown)
          → [ per task-step:
                plan → build → refactor → review → step-validate
                  ⇄ [ ship? ]      # shippable: forge-miss → ship → re-validate (before PASS)
              ]
          → task-validate
          ⇄ [ ship? ]              # ship_after = task_validate: same forge loop
        ]
  → slice validate
  → slice delivered              # residual ship boundary → rr-ci when nothing shipped mid-slice
```

Prepare phases (task-list, task detail) remain **rr-prepare**. Orchestrate routes there when the cursor is still in prep (no detailed buildable work yet).

## Task-step stage contracts

| Stage | What builder does | Loads | Executes code? | Done-when |
|-------|-------------------|-------|----------------|-----------|
| **plan** | Ensure feature branch ([feature-branch.md](feature-branch.md)), then produce/enrich step plan + assessment only | [plan-knowledge.md](plan-knowledge.md) allowlist (includes feature-branch) | **No** app source (git branch create/checkout OK) | Branch settled + sidecar `{NNNN}-{step}.plan.md` complete per [plan-schema.md](plan-schema.md) (Verify = checkboxes; incl. **Ship**); set `step_plan_done: true` |
| **build** | Implement the step | Current `{NNNN}-{step}.plan.md` + minimal task Goal/Obligations if needed; full **rr-coder** + **rr-tester** (code **and** tests for the step). **Do not** Read other steps’ `.plan.md` files or inlined plan prose from the task body | **Yes** | Code + tests for the step land; step verify checks runnable; set `step_build_done: true` |
| **refactor** | Behavior-invariant coder-rule refactor on step **build-touched** MR scope | **rr-refactor** (`epoch_cap: 5` default) | Via inline fix path | Skip or converge + lean `{NNNN}-{step}.refactor.md` written; set `step_refactor_done: true` (see below) |
| **review** | Full multi-lane review with fix, endless until clear | **rr-review** with **`--fix --all --endless`** (forced) | Via review fix path | Endless exit success **and** task sidecar `{NNNN}-{step}.review.md` present; set `step_review_done: true` |
| **step-validate** / **task-validate** | Rubric + persist report; mark Verify checkboxes on item PASS | [task-validate.md](task-validate.md) | No (assessment) | Report at `{NNNN}-{step}.validate.md` / `{NNNN}.task-validate.md` with plan + per-item PASS/FAIL; forge-miss FAIL → **ship** then re-validate |
| **ship** | Resolve branch/base; hand off **rr-ci**; return to validate | [ship.md](ship.md) then `skills/rr-ci/SKILL.md` | Via rr-ci only | [ship.md](ship.md) done-when; set `step_ship_done: true` when step-scoped; re-enter validate |
| **slice validate** | Rubric: did **slice** hit slice goal / AC; persist report | [slice-validate.md](slice-validate.md) | No (assessment) | `docs/rr/tasks/{slice_id}/slice-validate.md` with plan + per-item PASS/FAIL |

### Stage procedures (orchestrate)

#### plan

| | |
|--|--|
| **Loads** | [plan-knowledge.md](plan-knowledge.md) only (includes [feature-branch.md](feature-branch.md), [plan-schema.md](plan-schema.md)) |
| **Inputs** | `{NNNN}.md` Steps item at `step_index`; slice kernel for context if needed |
| **Durable output** | `docs/rr/tasks/{slice_id}/{NNNN}-{step}.plan.md` + Steps pointer `→ plan: \`…\`` |
| **Done-when** | Branch settled; six sections present; **Verify hooks** are `- [ ]` checkboxes; `step_plan_done: true` |
| **Hard-stops** | Still on `main`/`master` without ensure; missing Ship; Verify as free prose |
| **Nested** | None (knowledge allowlist — not rr-coder) |

#### build

| | |
|--|--|
| **Loads** | Current `{NNNN}-{step}.plan.md` (only plan among plans); thin Goal/Obligations; `rr-coder/SKILL.md` + `rr-tester/SKILL.md` |
| **Inputs** | Plan Goal/Approach/Verify hooks; allowlisted code/test refs as coder/tester require |
| **Durable output** | Application source + tests (no new task sidecar required) |
| **Done-when** | Step code+tests land; Verify hooks runnable; `step_build_done: true`; `step_build_base_sha` recorded at build start (`git rev-parse HEAD` before the first build commit) |
| **Hard-stops** | Missing plan sidecar; inventing scope beyond Non-goals |
| **Nested** | **rr-coder**, **rr-tester** |

#### refactor

| | |
|--|--|
| **Loads** | `rr-refactor/SKILL.md`; scope rule below |
| **Inputs** | MR ∩ **build-touched** paths; `epoch_cap: 5` |
| **Scratch** | Optional `.ai/refactor/<runId>/` (`state.json`, epochs) — not durable SoT |
| **Durable output** | `docs/rr/tasks/{slice_id}/{NNNN}-{step}.refactor.md` (lean note); optional `→ refactor:` pointer |
| **Done-when** | Empty intersection → skip note + `step_refactor_done: true`; else converge/skip-or-partial + lean note written + `step_refactor_done: true` |
| **Hard-stops** | Collector/verify unrecoverable stop per rr-refactor (ends chain) |
| **Nested** | **rr-refactor** (`--refactor` handoff: chat lean summary only, no required `report.md`) |

#### review

| | |
|--|--|
| **Loads** | `rr-review/SKILL.md`; force `--fix --all --endless` |
| **Inputs** | Step MR/workspace scope; brief sources; `max_epochs` default 5 |
| **Scratch** | `.ai/review/<runId>/` (brief/assess/challenge/`report.md`) |
| **Durable output** | `docs/rr/tasks/{slice_id}/{NNNN}-{step}.review.md`; optional `→ review:` pointer |
| **Done-when** | Endless success (clear or warnings-security-only, residual probe clean) **and** task review sidecar `{NNNN}-{step}.review.md` on disk; **then** set `step_review_done: true` |
| **Hard-stops** | Epoch cap without clear; unchallenged report; empty allowlist; endless “success” chat without writing the task sidecar; setting `step_review_done` / advancing without sidecar present |
| **Nested** | **rr-review** → rr-coder / rr-tester / rr-security-auditor lanes |

#### step-validate / task-validate

| | |
|--|--|
| **Loads** | [task-validate.md](task-validate.md) |
| **Inputs** | Plan Verify checkboxes (step) or task Verify/Goal/Obligations (task); Ship block; evidence from prior stages |
| **Durable output** | `{NNNN}-{step}.validate.md` or `{NNNN}.task-validate.md` — Validation plan + per-item PASS/FAIL |
| **Marking** | Item PASS → flip matching `- [x]` on plan/task Verify; FAIL leaves `- [ ]` (report SoT for FAIL) |
| **Done-when** | Report written; overall PASS only if all required items PASS; **shippable:** forge landing satisfied ([task-validate.md](task-validate.md) — push to open PR tip **or** carry-to-next) before cursor advance |
| **Hard-stops** | Non-forge FAIL; forge-miss → **ship** then re-enter (not a permanent stop under auto); advancing with orphaned validate sidecar (no open-PR push and no carry-to-next) |
| **Nested** | None (assessment); forge probe via **rr-ci** preflight when shippable |

#### ship

| | |
|--|--|
| **Loads** | [ship.md](ship.md) then `skills/rr-ci/SKILL.md` |
| **Inputs** | Plan **Ship** (`branch` / `ship_after` / `base`) |
| **Durable output** | Open PR/MR via rr-ci; `active_ship_branch` / `ship_base_branch` on summary |
| **Done-when** | [ship.md](ship.md); `step_ship_done: true` when step-scoped; return to validate |
| **Hard-stops** | rr-ci failure / missing branch |
| **Nested** | **rr-ci** |

#### slice validate

| | |
|--|--|
| **Loads** | [slice-validate.md](slice-validate.md) |
| **Inputs** | Kernel + task-summary + all `{NNNN}.task-validate.md` PASS |
| **Durable output** | `docs/rr/tasks/{slice_id}/slice-validate.md` |
| **Done-when** | Report PASS → `builder_stage: delivered` |
| **Hard-stops** | Any rubric FAIL → leave `slice_validate` |
| **Nested** | None |

### Knowledge load vs full-skill handoff

| Stage / mode | Behavior |
|--------------|----------|
| **plan** (orchestrate) | **Read** [plan-knowledge.md](plan-knowledge.md). Run [feature-branch.md](feature-branch.md) ensure **first**. Then load remaining allowlist refs in **one parallel** tool turn ([plan-knowledge.md](plan-knowledge.md)). Emit plan per [plan-schema.md](plan-schema.md) to `{NNNN}-{step}.plan.md`. Do **not** run rr-coder/rr-tester implement procedures. |
| **build** (orchestrate) | **Read** current step plan `{NNNN}-{step}.plan.md` (read-budget: this file only among plans), optional thin task Goal/Obligations, then nested `rr-coder/SKILL.md` **and** `rr-tester/SKILL.md` in **one parallel** turn. Prefer step Verify hooks over full tester flag-routing when orchestrate already scoped the step. |
| **refactor** (orchestrate) | **Read** `rr-refactor/SKILL.md` with scope resolved below; default `epoch_cap: 5`. Durable: lean `{NNNN}-{step}.refactor.md`. Mid-flight migration: if entering refactor with `step_review_done: true`, after refactor done-when **reset** `step_review_done: false` so review re-runs on cleaned code. |
| **review** (orchestrate) | **Read** `rr-review/SKILL.md`; force `--fix --all --endless` regardless of user omission. Pass `max_epochs` (default 5). Durable terminal: `{NNNN}-{step}.review.md` (scratch under `.ai/review/`). |
| **ship** (orchestrate) | **Read** [ship.md](ship.md), then `skills/rr-ci/SKILL.md`. Do **not** invent forge CLI in builder. |
| Explicit lane flag | Full-skill **handoff** — see [routing.md](routing.md). No pipeline advance past that skill’s done-when. |

## Cursor persistence (minimal v1)

Prefer extending existing prepare artifacts — no third parallel state file.

| Field | Where | Values / notes |
|-------|--------|----------------|
| `builder_stage` | `{NNNN}.md` frontmatter (active task) and/or `task-summary.md` | `prepare` \| `plan` \| `build` \| `refactor` \| `review` \| `step_validate` \| `ship` \| `task_validate` \| `slice_validate` \| `delivered` |
| `step_index` | `{NNNN}.md` frontmatter | 0-based index into that task’s **Steps** (omit when stage is prepare / task_validate / slice_validate / delivered) |
| `step_plan_done` | `{NNNN}.md` frontmatter | `true` \| `false` — applies to current `step_index`; reset to `false` when advancing `step_index` |
| `step_build_done` | `{NNNN}.md` frontmatter | `true` \| `false` — same scope as `step_plan_done` |
| `step_refactor_done` | `{NNNN}.md` frontmatter | `true` \| `false` — same scope as `step_plan_done`; reset when advancing `step_index` |
| `step_review_done` | `{NNNN}.md` frontmatter | `true` \| `false` — same scope as `step_plan_done`; may be reset to `false` after mid-flight refactor migration (see below) |
| `step_ship_done` | `{NNNN}.md` frontmatter | `true` \| `false` — step-scoped ship; treat as `true` when plan `ship_after: never` (non-shippable — nothing to ship; does **not** waive Goal/Verify). Reset when advancing `step_index` |
| `step_build_base_sha` | `{NNNN}.md` frontmatter | Commit SHA captured at **build** start (`git rev-parse HEAD` before the first build commit). SoT for refactor's build-touched scope (see Orchestrate refactor scope rule). Reset to empty when advancing `step_index` |
| `active_ship_branch` | `task-summary.md` | Last resolved ship head branch (from plan Ship / feature-branch) |
| `ship_base_branch` | `task-summary.md` | Last resolved PR/MR base (`default` branch name or prior open tip) |
| `prepare_status` | `task-summary.md` | Existing: `l1` \| `l2` \| `complete` — still authoritative for prep completeness |

Update fields when a stage’s done-when passes — **before** looping or stopping. Do not invent a second cursor store. Do **not** infer plan/build/refactor/review/ship completion from prose alone — use the booleans (+ Ship section for whether ship applies).

### Orchestrate refactor scope rule

When stage is **refactor** (not `--refactor` handoff):

1. Resolve MR file list (rr-review MR recipe in `rr-review/refs/params.md`).
2. Narrow to files touched during the current step's **build** only, from the pre-build snapshot: cursor `step_build_base_sha` (recorded at build start per the Cursor persistence table). **Do not** intersect with review-touched paths.
3. **Empty intersection** → **skip** refactor with lean `{NNNN}-{step}.refactor.md` (status `skipped`) or chat skip note; set `step_refactor_done: true` — do **not** stop the slice.
4. Pass resolved scope as `payload.refactor.paths` + `scope: MR` + `epoch_cap: 5` to **rr-refactor**.

**Build-touched scope helper** (stdout → value only; mirrors the rr-test-endless helper pattern):

```bash
# Requires step_build_base_sha from {NNNN}.md frontmatter (required field when build ran).
comm -12 \
  <(git diff --name-only "${STEP_BUILD_BASE_SHA}...HEAD" | sort -u) \
  <(printf '%s\n' "${STEP_PATH_HINTS[@]}" | sort -u)
# stdout = intersected repo-relative path list → payload.refactor.paths. Empty output = skip refactor.
```

Missing `step_build_base_sha` when build ran → treat as a hard-stop cursor gap (stop with a one-line reason); do not recompute the base from prose or guesses.

### Mid-flight migration (review-before-refactor → refactor-before-review)

If cursor shows `step_review_done: true` and `step_refactor_done: false` (legacy order mid-flight):

1. Run **refactor** per scope rule above.
2. After refactor done-when (or skip), **reset** `step_review_done: false`.
3. Next probe picks **review** so review re-runs on cleaned code.

## Cursor algorithm

Probe order — **first match wins** (this is the **next** stage for `scope: next`, and the head of the remaining path for `scope: step` / `task` / `slice`). Read only frontmatter fields above + current step plan **Ship** when noted — do **not** invent completion from scanning step markdown narrative.

1. **No pin-complete kernel / no `slice_id`** → stop or AskQuestion (need plan freeze / path).
2. **Missing / incomplete prepare** (`outlined` rows, or `prepare_status` ≠ `complete`) → stage **prepare** → load **rr-prepare**.
3. **Active task** has next **task-step** with `step_plan_done` ≠ `true` → **plan**.
4. **`step_plan_done: true` and `step_build_done` ≠ `true`** → **build**.
5. **`step_build_done: true` and `step_refactor_done` ≠ `true`** → **refactor** (full **rr-refactor** per scope rule above; apply mid-flight migration reset after done-when when prior `step_review_done` was `true`).
6. **`step_refactor_done: true` and `step_review_done` ≠ `true`** → **review** (`--fix --all --endless`).
7. **`step_review_done: true`** → **step-validate** (until PASS recorded for this step).
8. **While on step-validate** — Run [task-validate.md](task-validate.md) for step scope (incl. Ship-intent review when `never`; Forge/PR when shippable). Branch table:

   | Condition | Action |
   |-----------|--------|
   | **Forge / PR FAIL** ∧ `ship_after: step_validate` ∧ `step_ship_done` ≠ `true` | **Ship** ([ship.md](ship.md)); after ship done-when → return here (re-validate). Under `drive: auto`, chain ship → re-validate without asking. |
   | Other **FAIL** | Leave `builder_stage: step_validate`; hard-stop chaining under `scope: step\|task\|slice`. |
   | **PASS** ∧ `ship_after: never` | `step_ship_done` satisfied → go to 9. |
   | **PASS** ∧ shippable | Open PR already proven; `step_ship_done` should be `true`. Satisfy **forge landing** ([task-validate.md](task-validate.md) Forge landing — rr-ci push validate+cursor docs onto open tip, **or** carry-to-next) → go to 9. Do **not** enter ship-after-PASS for the forge-miss gate (`ship_after: step_validate` create path stays before PASS). |

9. **Advance** — Only after forge landing (shippable) or never-ship path:

   | Condition | Action |
   |-----------|--------|
   | More steps remain | Next `step_index`; set `step_plan_done` / `step_build_done` / `step_refactor_done` / `step_review_done` / `step_ship_done` to `false` (also reset `step_build_base_sha`). |
   | No more steps | **Task-validate** (under `scope: step`, still in-boundary — do **not** stop; continue into step 10). |

10. **While on task-validate** — Same forge loop for any step plan with `ship_after: task_validate` and ship not done (AskQuestion once if several Ship blocks). Branch table:

   | Condition | Action |
   |-----------|--------|
   | Other **FAIL** | Hard stop. |
   | **PASS** | Satisfy **forge landing** for the task-validate report ([task-validate.md](task-validate.md) Forge landing — including when no step used `ship_after: task_validate`, land onto **last open step Ship PR** / `active_ship_branch`). |
   | **Final task-step close** | Tip (or carry-to-next) must include **both** last-step `{NNNN}-{step}.validate.md` and `{NNNN}.task-validate.md` before stopping `scope: step` / `task` (SoT: Scope stop boundaries below). → next task or step 11. |
   | **Feature mode: PASS** (+ forge landing) or hard FAIL | **Stop** (do not go to step 11). Under `scope: step`, task-validate PASS + forge landing is the stop boundary when this was the final task-step (or when the run entered with cursor already on `task_validate`). |
11. **All tasks validated** → **slice validate** (orchestrate `scope: slice` only — skip under feature).
12. **Slice validate PASS** → stop: **slice delivered** → point engineer to **rr-ci** only for residual unshipped work (do **not** open PR from builder). Mid-slice ships already handed off via **ship**.

Explicit lane flag wins over this cursor even if `builder_stage` says otherwise ([input-resolution.md](input-resolution.md)).

**Endless review hard-stop:** if review exits at `--max-epochs` without clear/warnings-security-only → leave `step_review_done` unset; hard-stop the orchestrate chain (do not advance to step-validate).

**Review sidecar hard-stop:** never set `step_review_done: true` and never advance past review unless `docs/rr/tasks/{slice_id}/{NNNN}-{step}.review.md` exists after endless success. Missing sidecar = incomplete review (treat as hard-stop, not a soft skip).

## Scope stop boundaries

**SoT for scope stop boundaries + last-step equivalence.** Other sites (SKILL.md, README, routing.md) carry one-line pointers only — update this table first, then pointers. Forge-landing mechanics SoT: [task-validate.md](task-validate.md) Forge landing.

| `scope` | Stop when |
|---------|-----------|
| `next` | Cursor-next stage done-when met (no chaining) |
| `step` | **Non-final** task-step: step-validate PASS + forge landing (incl. ship→re-validate if shippable). **Final** task-step (no more steps after advance), **or** cursor already on `task_validate`: continue through **task-validate PASS** + forge landing of **both** last-step and task validate sidecars onto tip — same stop as `scope: task` for that run. If cursor is still **prepare**, complete prepare then stop (do not enter first step). **Anti-trigger:** do **not** park `builder_stage: task_validate` and exit `--step` after the last step’s step-validate PASS; do **not** stop `--step`/`--task` with validate docs only on disk. |
| `task` | Active task reaches task-validate PASS + forge landing (all its steps + task-validate). **Feature mode** always uses this boundary and **must not** advance to slice-validate / delivered. |
| `slice` | Slice validate PASS → delivered (or hard stop). Replaces retired `--full`. Not used under `--feature`. |

**Last-step equivalence:** On the final task-step, `scope: step` ≡ `scope: task` through task-validate PASS **and** forge landing of last-step + task validate reports onto the open tip (or carry-to-next) — then stop (do not enter next task / slice-validate). Mid-task steps keep the narrower step-validate + forge-landing boundary.

## Readiness set (`drive: manual`, `scope: slice`)

From the cursor algorithm over **remaining** stages until **delivered**:

| Class | Rule |
|-------|------|
| **ready** | Stage whose prior done-when is met (no open prereq) — runnable now |
| **blocked** | Stage whose prior done-when is unmet — list with prereq for guidance; **not** offered as runnable |
| **`(next)`** | Suffix on the ready item that the cursor algorithm would pick under `scope: next` — exactly one label when a next stage exists |

Linear pipeline usually yields **one** ready stage (that item is also **`(next)`**). Still list the remaining blocked path. AskQuestion **only** among the ready set — never offer blocked stages as executable choices. When presenting the ready list (AskQuestion options or prose), mark that cursor stage as e.g. `build (next)` so the engineer sees which choice `--next` would have run. Under `manual` × `step` / `task`, present only stages within the current scope boundary the same way.

## Isolated step run (`auto` × `task` \| `slice`)

**When:** `payload.mode: orchestrate` ∧ `drive: auto` ∧ `scope: task|slice` (includes lone `--task` / `--slice`). Cursor is inside a remaining **task-step** (plan→…→step-validate), not prepare / task-validate / slice-validate / delivered.

**Out of this cell:** `--feature` (parent-inline), `--manual`, `--auto --next`, `--auto --step`, explicit lane handoffs.

**Isolation:** context only — **same working tree**; never parallel steps; never `git worktree`.

### Ownership

| Owner | Owns |
|-------|------|
| **Parent** | resolve / mode / load; **prepare**; spawn one `generalPurpose` Task per remaining task-step; **dirty-tree gate** after each return; **ship** / **rr-ci**; **task-validate**; **slice-validate** + delivered (`scope: slice` only) |
| **Executor** | That task-step’s inner pipeline `plan → build → refactor → review → step-validate` (resume from cursor `builder_stage` / `step_*_done`). Spec: [executors/step.md](executors/step.md). Prompt: [templates/step-task.template.md](templates/step-task.template.md). |

Parent does **not** implement the step inline under this cell ([routing.md](routing.md) anti-pattern).

### Loop

```
parent: prepare if needed
  → while remaining task-steps in scope:
       spawn generalPurpose Task (step executor) for current step_index
       ← Task returns status ok | needs_ship | failed
       dirty-tree gate (git status --porcelain)
         dirty or failed → hard-stop (list paths; do not spawn next; do not silent-commit)
         clean + needs_ship → parent ship → re-run step-validate inline (assessment only)
             → parent commits cursor/validate → dirty-tree gate → continue
         clean + ok → if forge miss already handled / no ship needed → next step or exit loop
  → parent task-validate (+ forge landing)
  → scope slice only: parent slice-validate → delivered
```

### Dirty-tree gate

After each Task return (and after parent post-ship commit), parent runs `git status --porcelain`.

| Porcelain | Action |
|-----------|--------|
| **Non-empty** | Hard-stop: list dirty paths; do **not** spawn the next step; do **not** silent-commit. Under this cell, **carry-to-next does not waive** a dirty tree ([task-validate.md](task-validate.md) isolation exception). |
| **Empty** | Continue (next spawn, or parent ship / task-validate). |

**Success path:** executor **commits** step work (app source + this step’s durable sidecars + cursor flags) **before** return so porcelain is empty.

**Failure path:** executor must **not** commit; dirty tree is expected; parent stops.

### `needs_ship`

Executor may return `needs_ship` after writing/committing a forge-miss step-validate report (forge POST stays in parent). Parent runs [ship.md](ship.md) → **rr-ci**, re-runs step-validate **inline** (assessment only), commits cursor/validate, dirty-gates, then spawns the next step Task (or proceeds to task-validate).

### Nested-skill leaf Tasks

CE parent-only executors normally forbid nested Task. Contract here: the step executor **is** the parent session for nested lane skills — leaf Tasks those skills already document (`refactor-collector`, tester agents, etc.) stay allowed. Executor MUST NOT re-invoke **rr-builder**, MUST NOT spawn sibling step Tasks, MUST NOT run `--add-endless-test`.

## Orchestrate run loop (drive × scope)

Resolve `payload.drive` / `payload.scope` defaults in [input-resolution.md](input-resolution.md). Then:

```
resolve flags + cursor
  → probe cursor / readiness set
  → decide drive × scope:
       auto × next  → execute next stage → stop at done-when
       auto × step  → execute → re-probe → repeat until step boundary (or hard stop)
       auto × task  → Isolated step run (above) until task-validate PASS (or hard stop)
       auto × slice → Isolated step run (above) then task-/slice-validate until delivered (or hard stop)
       manual × next → show next stage (AskQuestion confirm/edit) → execute that one → stop
       manual × step|task|slice → AskQuestion before each stage; under slice keep ready-vs-blocked with (next); stop at scope boundary
```

| Cell | Behavior |
|------|----------|
| **auto × next** | Run cursor-next stage (may load multiple nested skills/refs **in order** within that stage’s done-when). Persist cursor. **Stop** — do not chain. |
| **auto × step** | Same execute as next, then **loop** until the **step** scope boundary (non-final → step-validate PASS + forge landing; final step or cursor on `task_validate` → task-validate PASS + forge landing of last-step + task reports). If cursor is **prepare**, complete prepare then **stop** (do not enter first step). Parent-inline (not Isolated step run). |
| **auto × task** | **Isolated step run** (above): one sequential step Task per remaining task-step → dirty-tree gate → parent task-validate (+ ship as needed) until task-validate PASS, or hard stop. |
| **auto × slice** | **Isolated step run** across remaining tasks’ steps, then parent task-validate / slice-validate → **delivered**, or hard stop (validate FAIL, missing kernel, dirty-tree gate, refactor stop, endless review max-epochs, user cancel). Silent chaining requires `drive: auto`. |
| **manual × next** | Present only the next logical stage; wait for confirm/change; execute that one; then wait again or stop if user declines. **Never** execute without confirm. |
| **manual × step** / **task** / **slice** | Same boundaries as auto counterparts; AskQuestion before each stage execute. Under `slice`, list remaining stages as **ready** vs **blocked** (+ prereq); mark the cursor stage **`(next)`**; AskQuestion among **ready** only; execute chosen; re-list until decline / delivered / hard stop / boundary. **Never** offer blocked as runnable. Parent-inline (not Isolated step run). |

**Hard stop** ends any loop: stage failure, validate FAIL, dirty-tree gate (isolation cell), missing inputs, conflicting flags, endless review epoch cap without clear exit, user decline. Persist `builder_stage` / `step_index` / `step_*_done` after each successful done-when before the next probe.

**Handoff:** skip this loop — [routing.md](routing.md) handoff table; stop at nested done-when. Drive/scope do not mutate handoff lanes.

**Feature:** after [feature.md](feature.md) mint + cursor, run this loop with `scope: task` and paths under `artifact_root` **parent-inline** (not Isolated step run); hard-stop at task-validate (step 10) — never slice-validate / delivered.
