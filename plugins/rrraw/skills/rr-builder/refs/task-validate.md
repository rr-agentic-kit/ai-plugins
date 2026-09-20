# Task validate rubric

**Audience:** `rr-builder` orchestration for **step-validate** (per task-step) and **task-validate** (after all steps). Assessment only — no application source edits.

## Inputs

| Input | Source |
|-------|--------|
| Task artifact | `docs/rr/tasks/{slice_id}/{NNNN}.md` |
| Goal / Obligations / Verify | Task body (task-validate) or current step plan Goal / Verify hooks (step-validate) |
| Ship block | Current `{NNNN}-{step}.plan.md` **Ship** (step-validate); any step with pending `ship_after: task_validate` (task-validate) |
| Evidence | Diffs, test results, step notes from build/review; forge probe when shippable |

## Rubric

| Check | PASS when | FAIL when |
|-------|-----------|-----------|
| **Goal** | Observable Goal outcome is met in the working tree / runnable verify | Goal unmet or only partially delivered without explicit Non-goals carve-out |
| **Verify / done** | Every Verify / done criterion is evidenced (command output, artifact, or cited proof) | Any Verify item missing, skipped, or contradicted |
| **Obligations** | Cited constitution / tech ADR / delta obligations still hold for changed surfaces | Obligation violated or silently ignored |
| **Non-goals** | Non-goals were not implemented as scope creep | Non-goal work shipped as if in-scope |
| **Open risks** | Residual risks either closed or explicitly carried with owner | Blocking `pending_tech` / open risk ignored as if done |
| **Forge / PR** (shippable only) | `ship_after` ≠ `never` **and** an open PR/MR exists whose head is `Ship.branch` (probe via **rr-ci** preflight / forge CLI — do not invent flags in builder) | Shippable and no matching open PR/MR |
| **Ship intent** (`never` review) | `ship_after: never` fits a non-shippable step (no forge open intended this step) | `never` contradicts shippable intent (e.g. step clearly meant to open a PR) — AskQuestion once: keep `never` \| set `step_validate`/`task_validate` \| abort; do **not** invent a PR requirement for a confirmed `never` |

**Shippable** means plan `ship_after` is `step_validate` or `task_validate`. When `never`, skip the **Forge / PR** row entirely — Goal/Verify/Obligations/Non-goals/Open risks + **Ship intent** review only.

## Verdict

Emit one line: `step-validate: PASS | FAIL` or `task-validate: PASS | FAIL` plus ≤5 bullets of evidence (cite section + proof).

On **FAIL**:
- Leave `builder_stage` at `step_validate` or `task_validate`; do **not** advance `step_index` / next task / slice validate.
- If FAIL is **Forge / PR** only and `ship_after` matches this validate scope → next ready stage is **ship** ([ship.md](ship.md)); under `drive: auto`, enter **ship** then re-enter this validate stage.
- Other FAIL reasons → hard stop for `--full` chaining (do not auto-ship).

On **PASS** with `ship_after: never`: treat `step_ship_done` as satisfied for advance (nothing to ship).

## Out of scope

- Slice-level AC / execute-slice outcome → [slice-validate.md](slice-validate.md)
- Re-running full rr-review (already done at review stage)
- Inventing new acceptance criteria not in the task / step plan
- Opening PR/MR inside builder — **rr-ci** via **ship** only
