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
| Non-Sonar job failures | `debug-pipeline` then ad-hoc code/test fix |
| Sonar / quality findings | `/s-ci --fix --sonar` |

Do **not** invent `gh`/`glab` flags in builder. Follow `skills/s-ci/refs/pipeline-fix-rules.md` (no disable/bypass without AskQuestion).

## Wait

0. **Host monitor first:** when the host exposes a PR/CI monitor (a bound-PR status tool or CI-monitor events), read check state from it instead of starting a poll or watch loop beside it. Checks pending → record `pending` and wait for the host event. A single blocking watch (item 1) is allowed only when this invoke must return the result in-session.
1. Poll via s-ci `pre-merge-status <PR#>` (pass the PR number; the bare form can fail on some `gh` versions) until pipeline/checks leave the pending set. On GitHub, prefer the blocking `gh run watch <RUN_ID> --exit-status` ([s-gh/refs/cli.md](../../s-gh/refs/cli.md)) over a manual sleep/backoff loop — it is the allowlisted wait primitive precisely because ad hoc short-sleep polling is disallowed for agents.
2. Backoff ~30–60s between polls when no blocking watch command exists for the forge.
3. Wall timeout default ~30 min → hard-stop with one-line reason.
4. Pending CI is **wait**, not FAIL.
5. **Self-retrigger:** writing and pushing *this stage's own* `{NNNN}(-{step}).pr-validate.md` report (or any cursor-only commit) is itself a new commit. On repos whose CI listens to `synchronize`, that push starts a **new** run. Resolve it with the **closing commit** rule below instead of chasing every report push forever.

### Closing commit (report-only push)

The **closing commit** is the one that persists this stage's report + cursor and touches **only** durable sidecars (`{artifact_root}/**`, `task-summary.md`) — no code, tests, config or workflow files.

1. **Skip-safety probe** — the forge accepts a CI-skip token in the head commit message (GitHub `[skip ci]`; GitLab `[ci skip]`) **and** no required status checks are configured (protection/ruleset lookup returns none, or the forge reports the feature unavailable for this plan). Required checks that a skipped workflow cannot satisfy would block the merge, so a probe that is undecidable counts as **fail**.
2. Probe passes → append the token to the closing commit message. It starts no run; the evidence is the last **code-bearing** tip, whose SHA the report names.
3. Probe fails (or the commit includes any non-sidecar file, or a fix epoch is still open) → no token; watch the retrigger run to a terminal result before Done-when.

## Verdict / fix loop

| Outcome | Action |
|---------|--------|
| **PASS** | `verdict == ready` **or** pipeline/checks success with no blocking security/quality blockers per pre-merge envelope |
| **FAIL → Sonar / quality** | Hand off **`/s-ci --fix --sonar`** (PR-scoped Sonar owns commit/push + wait + re-enter until tip clean); on return success → treat wait as satisfied for that epoch; on hard-stop → FAIL with that reason. Do **not** double-push or invent a second wait loop around Sonar |
| **FAIL → other jobs** | `debug-pipeline` → ad-hoc code/test fix in working tree → s-ci update/push tip → re-enter wait |
| **FAIL → stale base** | Failure text names a value that differs from the default branch (version, lockfile, workflow drift) and the default branch tip is ahead of the branch's merge base → merge the default branch into the branch (host sync tool, else `git merge`; never rebase or force-push), re-run the local checks for the files the merge touched, push, re-enter wait |
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
- closing commit: skip-token (evidence SHA <sha>) | watched run <id>

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
- The **closing commit** (report + cursor) was pushed to the open tip, and either it carried the skip token (probe passed — the report names the code-bearing SHA that is the evidence) or the run it triggered reached a terminal **PASS**. A poll taken *before* the closing commit was pushed is not evidence for a tip that has a new run.
- `step_pr_validate_done: true` when step-scoped.

## Anti-trigger: report-push retrigger

Do **not** treat `gh pr view --json mergeable` (or any other cached merge-state field) as evidence of CI conclusion for the latest push — `mergeable` reflects diff conflicts, not check/pipeline status. Before declaring `scope: step` / `task` / `slice` closed, re-resolve pipeline/checks (`pre-merge-status`, or the forge run list) keyed to the **current** HEAD SHA, not the SHA that was true when an earlier poll passed. Exception: a skip-token closing commit starts no run, so key the check to the last code-bearing SHA and say so in the report.

## Hard-stops

- Non-Sonar unrecoverable failure
- Epoch cap (`5`) without PASS
- Wait wall timeout (~30 min default)
- Engineer decline (manual)

## Isolation-cell ownership

Under **Isolated step run** ([slice-pipeline.md](slice-pipeline.md)): **parent owns** pr-validation (with ship / post-`needs_ship` re-validate). Executor `ok` does **not** imply CI green. After clean `ok` or post-ship re-validate+commit, if open tip → parent pr-validate before next spawn / task-validate.

## Out of scope

- Opening PR/MR — **ship** → **s-ci**
- Goal/Verify assessment — [task-validate.md](task-validate.md)
- Builder-owned Sonar listing — stays **s-ci**
- Review `--ci` path — unchanged
