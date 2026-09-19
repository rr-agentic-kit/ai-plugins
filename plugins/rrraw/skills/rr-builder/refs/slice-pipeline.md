# Slice pipeline (builder orchestration)

**Audience:** `rr-builder` in **orchestrate** mode (drive/scope flags or no lane flag). SoT for lifecycle, task-step stage contracts, cursor, and drive×scope run loop. Handoff mode does **not** advance this pipeline beyond the explicit nested skill.

## Slice lifecycle

```
slice ready
  → task-list                    # rr-prepare L1
    → [ per task:
          task detail              # rr-prepare L2 (+ steps breakdown)
          → [ per task-step:
                plan → build → review → refactor(TBD) → step-validate
              ]
          → task-validate
        ]
  → slice validate
  → slice delivered              # handoff boundary → rr-ci
```

Prepare phases (task-list, task detail) remain **rr-prepare**. Orchestrate routes there when the cursor is still in prep (no detailed buildable work yet).

## Task-step stage contracts

| Stage | What builder does | Loads | Executes code? | Done-when |
|-------|-------------------|-------|----------------|-----------|
| **plan** | Produce/enrich step plan + assessment only | **Knowledge** from rr-coder (incl. architecture refs) and rr-tester — not a full implement run | **No** | Step has enough detail + assessment for build; **no** application source edits |
| **build** | Implement the step | Full **rr-coder** + **rr-tester** (code **and** tests for the step) | **Yes** | Code + tests for the step land; step verify checks runnable |
| **review** | Full multi-lane review with fix | **rr-review** with **`--fix --all`** (forced) | Via review fix path | Review run complete; fix applied per review |
| **refactor** | **TBD** | — | — | Stub: **skip** or stop with `refactor stage not specified` — do **not** invent procedure |
| **step-validate** / **task-validate** | Rubric: did the **task** achieve Goal / Verify | [task-validate.md](task-validate.md) | No (assessment) | PASS/FAIL against task Goal + Verify / done |
| **slice validate** | Rubric: did **slice** hit slice goal / AC | [slice-validate.md](slice-validate.md) | No (assessment) | PASS/FAIL against execute-slice / pinned AC |

### Knowledge load vs full-skill handoff

| Stage / mode | Behavior |
|--------------|----------|
| **plan** (orchestrate) | **Read** selected knowledge refs only (rr-coder Required Knowledge + architecture; rr-tester heuristics/contracts as needed for step assessment). Do **not** run rr-coder/rr-tester implement procedures. |
| **build** (orchestrate) | **Read** nested `rr-coder/SKILL.md` and `rr-tester/SKILL.md` and follow them for the step (code + tests). |
| **review** (orchestrate) | **Read** `rr-review/SKILL.md`; force `--fix --all` regardless of user omission. |
| Explicit lane flag | Full-skill **handoff** — see [routing.md](routing.md). No pipeline advance past that skill’s done-when. |

## Cursor persistence (minimal v1)

Prefer extending existing prepare artifacts — no third parallel state file.

| Field | Where | Values / notes |
|-------|--------|----------------|
| `builder_stage` | `{NNNN}.md` frontmatter (active task) and/or `task-summary.md` | `prepare` \| `plan` \| `build` \| `review` \| `refactor` \| `step_validate` \| `task_validate` \| `slice_validate` \| `delivered` |
| `step_index` | `{NNNN}.md` frontmatter | 0-based index into that task’s **Steps** (omit when stage is prepare / task_validate / slice_validate / delivered) |
| `prepare_status` | `task-summary.md` | Existing: `l1` \| `l2` \| `complete` — still authoritative for prep completeness |

Update fields when a stage’s done-when passes — **before** looping or stopping. Do not invent a second cursor store.

## Cursor algorithm

Probe order — **first match wins** (this is the **next** stage for `scope: next`, and the head of the remaining path for `scope: full`):

1. **No pin-complete kernel / no `slice_id`** → stop or AskQuestion (need plan freeze / path).
2. **Missing / incomplete prepare** (`outlined` rows, or `prepare_status` ≠ `complete`) → stage **prepare** → load **rr-prepare**.
3. **Active task** has next **task-step** without completed **plan** → **plan**.
4. **Plan done, build not done** → **build**.
5. **Build done, review not done** → **review** (`--fix --all`).
6. **Review done** → **refactor** stub (skip until specified) → **step-validate**; when all steps done → **task-validate**.
7. **All tasks validated** → **slice validate**.
8. **Slice validate PASS** → stop: **slice delivered** → point engineer to **rr-ci** (do **not** open PR from builder).

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

**Hard stop** ends any loop: stage failure, validate FAIL, missing inputs, conflicting flags, user decline. Persist `builder_stage` / `step_index` after each successful done-when before the next probe.

**Handoff:** skip this loop — [routing.md](routing.md) handoff table; stop at nested done-when. Drive/scope do not mutate handoff lanes.
