# Task validate rubric

**Audience:** `rr-builder` orchestration for **step-validate** (per task-step) and **task-validate** (after all steps). Assessment only — no application source edits.

## Persist paths (canonical)

Resolve under **`artifact_root`** when `payload.feature.artifact_root` is set; otherwise `docs/rr/tasks/{slice_id}/` ([slice-pipeline.md](slice-pipeline.md) Artifact root).

| Scope | Path |
|-------|------|
| **step-validate** | `{artifact_root}/{NNNN}-{step}.validate.md` (default root: `docs/rr/tasks/{slice_id}/`) |
| **task-validate** | `{artifact_root}/{NNNN}.task-validate.md` |

`{step}` is **1-based** (same as plan sidecar). Write the report **before** advancing cursor on PASS.

## Inputs

| Input | Source |
|-------|--------|
| Task artifact | `{artifact_root}/{NNNN}.md` |
| Goal / Obligations / Verify | Task body (task-validate) or current step plan Goal / **Verify hooks** checkboxes (step-validate) |
| Ship block | Current `{NNNN}-{step}.plan.md` **Ship** (step-validate); any step with pending `ship_after: task_validate` (task-validate) |
| Evidence | Diffs, test results, step notes from build/refactor/review; forge probe when shippable |

## Validation plan (derive checklist)

Build the report’s **Validation plan** from:

| Scope | Source items |
|-------|--------------|
| **step-validate** | Plan **Verify hooks** (`- [ ]` items) + Goal of step + Obligations (if cited for the step) + **Forge / PR** when shippable + **Ship intent** when `never` |
| **task-validate** | Task **Verify / done** checkboxes + Goal + Obligations + Open risks / Non-goals gates + **Forge / PR** for any pending `ship_after: task_validate` + **Ship intent** review when `never` |

Do **not** invent criteria absent from plan/task. Each plan/task checkbox becomes one report row.

## Rubric

| Check | PASS when | FAIL when |
|-------|-----------|-----------|
| **Goal** | Observable Goal outcome is met in the working tree / runnable verify | Goal unmet or only partially delivered without explicit Non-goals carve-out |
| **Verify hooks / Verify / done** | Every checklist criterion is evidenced (command output, artifact, or cited proof) | Any Verify item missing, skipped, or contradicted |
| **Obligations** | Cited constitution / tech ADR / delta obligations still hold for changed surfaces | Obligation violated or silently ignored |
| **Non-goals** | Non-goals were not implemented as scope creep | Non-goal work shipped as if in-scope |
| **Open risks** | Residual risks either closed or explicitly carried with owner | Blocking `pending_tech` / open risk ignored as if done |
| **Forge / PR** (shippable only) | `ship_after` ≠ `never` **and** an open PR/MR exists whose head is `Ship.branch` (probe via **rr-ci** preflight / forge CLI — do not invent flags in builder) | Shippable and no matching open PR/MR |
| **Ship intent** (`never` review) | `ship_after: never` fits a non-shippable step (no forge open intended this step) | `never` contradicts shippable intent (e.g. step clearly meant to open a PR) — AskQuestion once: keep `never` \| set `step_validate`/`task_validate` \| abort; do **not** invent a PR requirement for a confirmed `never` |

**Shippable** means plan `ship_after` is `step_validate` or `task_validate`. When `never`, skip the **Forge / PR** row entirely — Goal/Verify/Obligations/Non-goals/Open risks + **Ship intent** review only.

## Report body

```markdown
# Step validate — {NNNN} step {step}
# (or) # Task validate — {NNNN}

## Validation plan
- [ ] <derived item 1>
- [ ] <derived item 2>
…

## Results

| Item | Verdict | Evidence |
|------|---------|----------|
| <Verify hooks / done text or rubric row> | PASS \| FAIL | <cite proof> |
…

step-validate: PASS | FAIL
# (or) task-validate: PASS | FAIL
```

- Per-item column is **PASS** or **FAIL** only (no soft grades).
- Final line must be exactly `step-validate: PASS | FAIL` or `task-validate: PASS | FAIL`.
- Overall **PASS** only when **all** required items PASS.

## Checkbox marking

On each item **PASS** that maps to a plan **Verify hooks** or task **Verify / done** checkbox → flip that source item to `- [x]` in `{NNNN}-{step}.plan.md` or `{NNNN}.md`.

On item **FAIL** → leave source `- [ ]`; FAIL evidence lives in this report (report is SoT for FAIL).

Do not mark Goal/Obligations/Non-goals prose as checkboxes unless those sections already use checklist items.

## Verdict / cursor

On **FAIL**:
- Leave `builder_stage` at `step_validate` or `task_validate`; do **not** advance `step_index` / next task / slice validate.
- If FAIL is **Forge / PR** only and `ship_after` matches this validate scope → next ready stage is **ship** ([ship.md](ship.md)); under `drive: auto`, enter **ship** then re-enter this validate stage.
- Other FAIL reasons → hard stop for `scope: step|task|slice` chaining (do not auto-ship).

On **PASS** with `ship_after: never`: treat `step_ship_done` as satisfied for advance (nothing to ship).

Chat: announce the persisted path (`…validate.md` or `…task-validate.md`).

## Out of scope

- Slice-level AC / execute-slice outcome → [slice-validate.md](slice-validate.md)
- Re-running full rr-review (already done at review stage)
- Inventing new acceptance criteria not in the task / step plan
- Opening PR/MR inside builder — **rr-ci** via **ship** only
