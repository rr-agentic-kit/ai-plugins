# PR validation (post forge-landing)

**Audience:** `rr-builder` orchestrate after shippable **step-validate** / **task-validate** forge landing **pushed** an open tip. Wait for PR/MR pipeline clean; broken CI is remediable in-loop. Forge probes and Sonar remediations stay **rr-ci** — builder orchestrates only.

## When

| Condition | Action |
|-----------|--------|
| Forge landing **pushed** for this validate scope (open tip matches tip resolution in [task-validate.md](task-validate.md)) | Enter **pr-validate** before advancing `step_index` / next task / scope stop |
| `ship_after: never` | **Skip** — no open tip intended |
| Carry-to-next (no open PR to watch) | **Skip** — no tip to poll |
| No open PR/MR after tip resolution | **Skip** (same as carry-to-next) |

**Default:** Run after **both** step-validate and task-validate when forge landing pushed to an open PR. Do **not** invent a `--pr-validate` handoff lane.

## Loads

`skills/rr-ci/SKILL.md` — use forge nested recipes for:

| Need | rr-ci path |
|------|------------|
| Wait / status | `pre-merge-status` (or forge nested equivalent) |
| Non-Sonar job failures | `debug-pipeline` then ad-hoc code/test fix |
| Sonar / quality findings | `/rr-ci --fix --sonar` |

Do **not** invent `gh`/`glab` flags in builder. Follow `skills/rr-ci/refs/pipeline-fix-rules.md` (no disable/bypass without AskQuestion).

## Wait

1. Poll via rr-ci `pre-merge-status` until pipeline/checks leave the pending set.
2. Backoff ~30–60s between polls.
3. Wall timeout default ~30 min → hard-stop with one-line reason.
4. Pending CI is **wait**, not FAIL.

## Verdict / fix loop

| Outcome | Action |
|---------|--------|
| **PASS** | `verdict == ready` **or** pipeline/checks success with no blocking security/quality blockers per pre-merge envelope |
| **FAIL → Sonar / quality** | Hand off **`/rr-ci --fix --sonar`**; after remediations → rr-ci update/push tip → re-enter wait |
| **FAIL → other jobs** | `debug-pipeline` → ad-hoc code/test fix in working tree → rr-ci update/push tip → re-enter wait |
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
- `step_pr_validate_done: true` when step-scoped.

## Hard-stops

- Non-Sonar unrecoverable failure
- Epoch cap (`5`) without PASS
- Wait wall timeout (~30 min default)
- Engineer decline (manual)

## Isolation-cell ownership

Under **Isolated step run** ([slice-pipeline.md](slice-pipeline.md)): **parent owns** pr-validation (with ship / post-`needs_ship` re-validate). Executor `ok` does **not** imply CI green. After clean `ok` or post-ship re-validate+commit, if open tip → parent pr-validate before next spawn / task-validate.

## Out of scope

- Opening PR/MR — **ship** → **rr-ci**
- Goal/Verify assessment — [task-validate.md](task-validate.md)
- Builder-owned Sonar listing — stays **rr-ci**
- Review `--ci` path — unchanged
