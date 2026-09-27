# PR validation (post forge-landing)

**Audience:** `rr-builder` orchestrate after shippable **step-validate** / **task-validate** forge landing **pushed** an open tip. Wait for PR/MR pipeline clean; broken CI is remediable in-loop. Forge probes and Sonar remediations stay **s-ci** — builder orchestrates only.

## When

| Condition | Action |
|-----------|--------|
| Forge landing **pushed** for this validate scope (open tip matches tip resolution in [task-validate.md](task-validate.md)) | Enter **pr-validate** before advancing `step_index` / next task / scope stop |
| `ship_after: never` | **Skip** — no open tip intended |
| Carry-to-next (no open PR to watch) | **Skip** — no tip to poll |
| No open PR/MR after tip resolution | **Skip** (same as carry-to-next) |

**Default:** Run after **both** step-validate and task-validate when forge landing pushed to an open PR. Do **not** invent a `--pr-validate` handoff lane.

## Loads

`skills/s-ci/SKILL.md` — use forge nested recipes for:

| Need | s-ci path |
|------|------------|
| Wait / status | `pre-merge-status` (or forge nested equivalent) |
| Non-Sonar job failures | `/s-ci --fix <run URL>` or forge-direct `--fix` (policy: `refs/ci/fix/pipeline-fix.md`) |
| Sonar / quality findings | `/s-ci --fix --sonar` |

Do **not** invent `gh`/`glab` flags in builder. Follow `refs/ci/fix/pipeline-fix-rules.md` (no disable/bypass without AskQuestion). Invoke `/s-ci --fix` or forge-direct **s-gh** / **s-glab**.

## Wait

1. **GitHub + known run id** — `skills/s-gh/scripts/wait-run.py RUN_ID` `[--repo owner/repo]` (from `gh run list` or push output). Do **not** invent inline `gh run view` / `python -c` poll chains. Then run s-ci `pre-merge-status` once for the authoritative all-checks verdict (`verdict`, `blockers`).
2. **No run id** (GitLab or GitHub without a run id) — poll s-ci `pre-merge-status` until pipeline/checks leave the pending set (forge-neutral fallback).
3. Backoff ~30–60s between `pre-merge-status` polls (`wait-run.py` uses its own bounded `--interval`, default 30s).
4. Wall timeout default ~30 min (`wait-run.py --timeout`, default 1800s) → hard-stop with one-line reason.
5. Pending CI is **wait**, not FAIL.

## Verdict / fix loop

| Outcome | Action |
|---------|--------|
| **PASS** | `verdict == ready` **or** pipeline/checks success with no blocking security/quality blockers per pre-merge envelope |
| **FAIL → Sonar / quality** | Hand off **`/s-ci --fix --sonar`**; after remediations → s-ci update/push tip → re-enter wait |
| **FAIL → other jobs** | `/s-ci --fix <run URL>` → s-ci update/push tip → re-enter wait |
| **Unrecoverable** (non-Sonar) | Hard-stop with one-line reason |

**Epoch cap:** `epoch_cap: 5` (same as review). Each push→re-poll cycle counts one epoch. Hitting the cap without PASS → hard-stop.

Do **not** re-enter full **review** after a CI fix unless a later live miss demands it.

## Durable report

| Scope | Path |
|-------|------|
| **step** | `{artifact_root}/{NNNN}-{step}.pr-validate.md` |
| **task** | `{artifact_root}/{NNNN}.pr-validate.md` |

Short report only: wait outcome, fix epochs used, final PASS/FAIL. Resolve under `artifact_root` when set ([slice-pipeline.md](slice-pipeline.md) Artifact root).

```markdown
# PR validate — {NNNN} step {step}
# (or) # PR validate — {NNNN}

## Wait
- outcome: ready | timeout | pending-exit-fail
- polls: <n>

## Fix epochs
| Epoch | Branch | Summary |
|-------|--------|---------|
| 1 | sonar \| debug+adhoc | <one line> |
…

pr-validate: PASS | FAIL
```

## Cursor

| Field | Rule |
|-------|------|
| `builder_stage` | `pr_validate` while in this stage |
| `step_pr_validate_done` | `true` on step-scoped PASS; reset to `false` when advancing `step_index` |
| Task-scoped done | Via leaving `pr_validate` after task report PASS (no separate task boolean required) |

Mid-flight cursors without `pr_validate` / missing `step_pr_validate_done`: treat as **not done** when an open tip was just landed this run.

## Done-when

- Report written with overall **PASS**.
- Tip still includes prior validate sidecars (re-push after fixes if dirty).
- **While the PR is still open:** this stage's own report + cursor flip (`step_pr_validate_done: true`) committed and pushed onto that PR's tip via s-ci — this push is pr-validate's closing act; it is what makes the PR merge-ready, not paperwork left for later.
- `step_pr_validate_done: true` when step-scoped.

## Premature merge

If pr-validate is entered and finds the PR **already merged/closed** — meaning the push above never happened before the PR closed — this is a **process anomaly**, not routine [task-validate.md](task-validate.md) carry-to-next (that fallback is scoped to step-/task-validate reports on a not-yet-opened tip, not this stage's own report on a tip that closed out from under it). Announce the anomaly in chat, still evaluate CI evidence retroactively (forge checks on the merged PR) for PASS/FAIL, then hand off to **s-ci** for a minimal docs-only commit scoped to this step's report + cursor flip alone (direct push to the base branch when allowed; else the smallest possible follow-up PR). Do **not** defer that commit into the next step's feature branch or ship — this step closes its own paperwork.

## Hard-stops

- Non-Sonar unrecoverable failure
- Epoch cap (`5`) without PASS
- Wait wall timeout (~30 min default)
- Engineer decline (manual)

## Isolation-cell ownership

Under **task run** ([task-run.md](task-run.md)): **pr-validate runs in a phase Task** ([executors/phase.md](executors/phase.md), `phase: pr_validate`). Parent spawns after task-validate PASS + forge landing push; parent does **not** inline CI wait/fix logs. Validate phase `ok` does **not** imply CI green. After post-ship re-validate+commit, if open tip → spawn pr-validate phase Task before scope stop / next task.

**Step-mode** (`--step`, mid-flight step granularity): parent-inline pr-validate unchanged ([slice-pipeline.md](slice-pipeline.md)).

## Out of scope

- Opening PR/MR — **ship** → **s-ci**
- Goal/Verify assessment — [task-validate.md](task-validate.md)
- Builder-owned Sonar listing — stays **s-ci**
- Review `--ci` path — unchanged
