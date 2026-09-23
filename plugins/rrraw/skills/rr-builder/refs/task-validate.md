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

### Forge landing (shippable PASS)

**SoT for forge-landing rules** (tip resolution, "both sidecars" final-task-step close, carry-to-next) — slice-pipeline.md, ship.md, routing.md, SKILL.md, and README point here; update this section first.

Validate writes the report **after** the forge-miss → **ship** → re-validate loop. Disk persist alone is not enough — sidecars + Verify checkbox flips must **land on forge** or be **carried to the next ship**.

**Tip resolution (which PR head):**

| Validate scope | Prefer tip |
|----------------|------------|
| **step-validate** | Current step plan `Ship.branch` when shippable; else `active_ship_branch` from `task-summary.md` |
| **task-validate** | Any pending `ship_after: task_validate` plan’s `Ship.branch`; **else** (all steps used `step_validate` / `never`) → **last open step Ship PR** = `active_ship_branch` or the latest still-open PR whose head matches a step `Ship.branch` in this task |

| Situation | Required action before advancing `step_index` / next task / declaring `scope: step\|task` complete |
|-----------|-----------------------------------------------------------|
| Open PR/MR whose head matches tip resolution above | Hand off **rr-ci** update/push so the validate sidecar(s) written this stage, flipped Verify checkboxes, and cursor frontmatter are on that tip. **Final task-step / task-validate:** tip **must** receive **both** `{NNNN}-{step}.validate.md` (last step) **and** `{NNNN}.task-validate.md` (+ cursor) before scope stop — push in one rr-ci handoff when both are dirty. |
| No open PR (e.g. already merged) and those paths are dirty/uncommitted | **Carry-to-next:** leave them dirty (or note them); next [feature-branch.md](feature-branch.md) ensure **must** carry them onto the new `feat/…` branch; next **ship** **must** include them in the rr-ci commit set. Do **not** invent a dedicated PR solely for validate docs |

**Probe (done-when):** tip contains the required sidecar(s) for this stage **or** carry-to-next was applied and announced. For last-step / task close under `scope: step` or `task`: tip (or carry set) includes `{NNNN}.task-validate.md` **and** the final `{NNNN}-{step}.validate.md`.

**Stop-rule:** Do **not** treat shippable step/task-validate as closed (do **not** advance cursor / stop `--step`/`--task`) while the validate sidecar(s) (+ matching Verify checkbox flips) are uncommitted **and** absent from the open PR tip **and** carry-to-next was not applied.

**Anti-trigger:** Do **not** claim PASS-complete from chat alone when forge tip lacks the validate sidecar. Do **not** skip task-validate forge landing because no step had `ship_after: task_validate` — use tip resolution above.

Chat: announce the persisted path (`…validate.md` or `…task-validate.md`) **and** whether landing was **pushed** or **carry-to-next**.

**Next stage:** When landing was **pushed** to an open tip → **pr-validate** ([pr-validate.md](pr-validate.md)). When `never` or carry-to-next → skip pr-validate and advance per [slice-pipeline.md](slice-pipeline.md).

### Isolation-cell exception (`auto` × `task` \| `slice`)

**SoT for the dirty-porcelain / carry-to-next isolation exception** — slice-pipeline.md Dirty-tree gate, ship.md, and routing.md point here.

Under **Isolated step run** ([slice-pipeline.md](slice-pipeline.md)):

- **Dirty porcelain is a hard-stop** — parent must not advance / spawn the next step Task while `git status --porcelain` is non-empty. Carry-to-next does **not** waive this gate in this cell (other drive×scope cells keep carry-to-next).
- **Parent owns** task-validate (and post-`needs_ship` step-validate re-run) **and pr-validate** when an open tip was landed. After parent ship + inline re-validate, parent **commits** cursor/validate sidecars so the dirty-tree gate can PASS before the next spawn.
- Executor-owned step-validate may return `needs_ship` with a committed forge-miss report; forge POST stays in parent via [ship.md](ship.md).

## Out of scope

- Slice-level AC / execute-slice outcome → [slice-validate.md](slice-validate.md)
- Re-running full rr-review (already done at review stage)
- Inventing new acceptance criteria not in the task / step plan
- Opening PR/MR inside builder — **rr-ci** via **ship** only
- Rewriting Forge/PR PASS to mean “merged historically” instead of open tip or carry-to-next
- PR/MR pipeline wait/fix after tip push → [pr-validate.md](pr-validate.md)
