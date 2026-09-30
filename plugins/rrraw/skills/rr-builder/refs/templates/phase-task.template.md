# Phase Task prompt template

Fill placeholders; spawn as `generalPurpose` Task. Executor: `refs/executors/phase.md`.

Shape follows CE `templates/task-prompt.template.md`. Parent uses this under **task run** only (`drive: auto` ∧ `scope: task|slice`, `pipeline_granularity: task`).

```text
You are the phase executor for rr-builder task run. Non-interactive.
Write fence: per phase.md for phase={phase} only.
Do NOT invoke rr-builder. Do NOT spawn Tasks for a different phase. Do NOT run --add-endless-test.
Do NOT run ship/s-ci from validate (return needs_ship instead). pr_validate loads s-ci per pr-validate.md.
On success (ok|needs_ship): commit before return so porcelain is empty. On failed: do NOT commit.

## Caller Load
- PLUGIN_ROOT: {PLUGIN_ROOT}
- REPO_ROOT: {REPO_ROOT}
- slice_id: {slice_id}
- artifact_root: {artifact_root}
- NNNN: {NNNN}
- phase: {phase}
- builder_stage: {builder_stage}
- pipeline_granularity: task
- task_plan_done: {task_plan_done}
- build_unit_index: {build_unit_index}
- task_build_base_sha: {task_build_base_sha}
- task_refactor_done: {task_refactor_done}
- task_review_done: {task_review_done}
- task_ship_done: {task_ship_done}
- scope: {scope}

## Commit policy (caller-filled)
{COMMIT_POLICY}
Trailers (verbatim, last lines of every commit message):
{COMMIT_TRAILERS}

## Required refs (Read first under PLUGIN_ROOT)
1. skills/rr-builder/refs/executors/phase.md
2. skills/rr-builder/refs/task-run.md
3. skills/rr-builder/refs/slice-pipeline.md (stage contracts)
4. skills/rr-builder/refs/plan-knowledge.md (plan phase)
5. skills/rr-builder/refs/plan-schema.md
6. skills/rr-builder/refs/feature-branch.md
7. skills/rr-builder/refs/task-validate.md (validate phase)
8. skills/rr-builder/refs/pr-validate.md (pr_validate phase only)

## Lane refs (phase-conditional)
- phase=build → skills/s-coder/SKILL.md AND skills/s-tester/SKILL.md
- phase=refactor → skills/s-refactor/SKILL.md
- phase=review → skills/s-review/SKILL.md (force --fix --all --endless)
- phase=plan | validate → none of the lane SKILL.md files
- phase=pr_validate → skills/s-ci/SKILL.md via pr-validate.md procedure

## Variant inject (Read when present)
- {artifact_root}/{NNNN}.md
- {artifact_root}/{NNNN}.plan.md
- Build unit excerpt for phase=build (unit index {build_unit_index})

## Execution
1. Validate Caller Load per phase.md — missing required → status failed + clarifications
2. Run exactly one phase={phase} per task-run.md + slice-pipeline.md contracts
3. Nested lane leaf Tasks already documented by s-coder/s-tester/s-refactor/s-review stay allowed
4. On forge-miss at validate with shippable ship_after → write/commit report + cursor; return needs_ship
5. On validate PASS (or never-ship path) → commit; return ok
6. On pr_validate PASS → commit report + cursor; return ok
7. On hard-stop → do not commit; return failed

## Output (chat — keep tiny)
- status: ok|needs_ship|failed
- phase + builder_stage
- Clarifications (or none)
- commit SHA or dirty
- sidecar paths written this phase
- Do NOT paste the full review report into chat
```

**Placeholders**

| Token | Meaning |
|-------|---------|
| `{PLUGIN_ROOT}` | Absolute plugin root (rrraw) |
| `{REPO_ROOT}` | Absolute host repo root |
| `{slice_id}` | Active slice id |
| `{artifact_root}` | Durable task root |
| `{NNNN}` | Task id stem |
| `{phase}` | `plan` \| `build` \| `refactor` \| `review` \| `validate` \| `pr_validate` |
| `{build_unit_index}` | 0-based; required when `phase: build` |
| `{builder_stage}` / task-run `task_*_done` | Resume cursor fields |
| `{scope}` | `task` \| `slice` |
| `{COMMIT_POLICY}` | Parent fills from the session git contract: short why-focused message via HEREDOC; no `--no-verify`; amend only when a pre-commit hook auto-fixed the just-created unpushed commit; no push (except `pr_validate` fix-push); Edit tool over `sed -i` |
| `{COMMIT_TRAILERS}` | Attribution lines from the session's system reminder, verbatim; empty when none |

**Spawn rules:** `subagent_type: generalPurpose` only; **one** Task at a time per phase; never parallel build units; never `git worktree`.
