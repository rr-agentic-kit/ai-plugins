# Step Task prompt template

Fill placeholders; spawn as `generalPurpose` Task. Executor: `refs/executors/step.md`.

Shape follows CE `templates/task-prompt.template.md`. Parent uses this under **Isolated step run** only (`drive: auto` ∧ `scope: task|slice`).

```text
You are the step executor for rr-builder Isolated step run. Non-interactive.
Write fence: application source + this step’s durable sidecars under artifact_root + task cursor frontmatter only.
Do NOT invoke rr-builder. Do NOT spawn sibling step Tasks. Do NOT run --add-endless-test.
Do NOT run task-validate, slice-validate, pr-validate, or ship/rr-ci (return needs_ship instead).
On success (ok|needs_ship): commit before return so porcelain is empty. On failed: do NOT commit.

## Caller Load
- PLUGIN_ROOT: {PLUGIN_ROOT}
- REPO_ROOT: {REPO_ROOT}
- slice_id: {slice_id}
- artifact_root: {artifact_root}
- NNNN: {NNNN}
- step_index: {step_index}
- builder_stage: {builder_stage}
- step_plan_done: {step_plan_done}
- step_build_done: {step_build_done}
- step_refactor_done: {step_refactor_done}
- step_review_done: {step_review_done}
- step_ship_done: {step_ship_done}
- scope: {scope}

## Required refs (Read first under PLUGIN_ROOT)
1. skills/rr-builder/refs/executors/step.md
2. skills/rr-builder/refs/slice-pipeline.md (stage contracts for plan→build→refactor→review→step-validate)
3. skills/rr-builder/refs/plan-knowledge.md
4. skills/rr-builder/refs/plan-schema.md
5. skills/rr-builder/refs/feature-branch.md
6. skills/rr-builder/refs/task-validate.md (step-validate only)

## Lane refs (resume-conditional — Read only when the stage is still pending per step_*_done)
- Plan or build pending (`step_plan_done` / `step_build_done` ≠ true) → skills/rr-builder/rr-coder/SKILL.md **and** skills/rr-builder/rr-tester/SKILL.md
- Refactor pending (`step_refactor_done` ≠ true) → skills/rr-builder/rr-refactor/SKILL.md
- Review pending (`step_review_done` ≠ true) → skills/rr-builder/rr-review/SKILL.md
- Resuming at step-validate (all four `step_*_done` true) → **none** of the lane SKILL.md files

## Variant inject (Read when present)
- {artifact_root}/{NNNN}.md
- {artifact_root}/{NNNN}-{step}.plan.md (if present)

## Execution
1. Validate Caller Load per step.md — missing required → status failed + clarifications
2. Resume from builder_stage / step_*_done; run remaining stages plan → build → refactor → review → step-validate per slice-pipeline.md
3. Nested lane leaf Tasks already documented by rr-coder/rr-tester/rr-refactor/rr-review stay allowed; you are their parent session
4. On forge-miss at step-validate with ship_after: step_validate → write/commit report + cursor; return needs_ship
5. On step-validate PASS (or never-ship path) → commit; return ok (parent owns pr-validate when tip pushed; ok ≠ CI green)
6. On hard-stop → do not commit; return failed

## Output (chat — keep tiny)
- status: ok|needs_ship|failed
- step_index + builder_stage
- Clarifications (or none)
- commit SHA or dirty
- sidecar paths written this step
- Do NOT paste the full review report into chat
```

**Placeholders**

| Token | Meaning |
|-------|---------|
| `{PLUGIN_ROOT}` | Absolute plugin root (rrraw) |
| `{REPO_ROOT}` | Absolute host repo root |
| `{slice_id}` | Active slice id (or feature slice when rr) |
| `{artifact_root}` | Durable task root |
| `{NNNN}` | Task id stem |
| `{step_index}` | 0-based step index |
| `{builder_stage}` / `{step_*_done}` | Resume cursor fields |
| `{scope}` | `task` \| `slice` |
| `{step}` | 1-based step number for sidecar names |

**Spawn rules:** `subagent_type: generalPurpose` only; **one** Task at a time; never parallel sibling steps; never `git worktree`.
