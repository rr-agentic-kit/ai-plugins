---
name: rr-builder
description: Slice build orchestrator (drive×scope; default --auto --step), ad-hoc --feature run, or explicit lane handoff. Not rr-planner/rr-ci.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Task, AskUserQuestion, TodoWrite
---

# rr-builder

**Human overview:** [README.md](README.md)

## Purpose

**Orchestrate** building a pin-complete execute-slice for software engineers: prepare → per-task plan/build/refactor/review/validate → optional planned **ship** (rr-ci handoff) → **pr-validate** (CI wait/fix after tip push) → slice validate → **delivered** residual. Drive (`--auto` \| `--manual`) × scope (`--next` \| `--step` \| `--task` \| `--slice`) control confirm gates and how far one run advances. **`--feature`** mints one ad-hoc task (rr `docs/rr/tasks/` or non-rr `.ai/tasks/`) and runs to **task-validate** only. With an explicit lane flag, **hand off** to exactly one nested skill and stop (drive/scope ignored). **Durable** artifacts under `docs/rr/tasks/` or feature `artifact_root` (tasks, plan/refactor/review/validate/pr-validate sidecars). **Scratch:** `.ai/review/<runId>/`, `.ai/refactor/<runId>/` (in-run only; not terminal SoT).

## When to use

- Continue or resume a frozen slice (orchestrate: no lane flag; defaults `drive=auto`, `scope=step`)
- Ad-hoc feature without a prior prepare/slice chain (`--feature`)
- Run without confirms (`--auto`), only the cursor stage (`--next`), one task-step (`--step`; final step ≡ `--task`), one task (`--task`), or until delivered (`--slice`)
- Explicit single-lane work: `--prepare` / `--coder` / `--tester` / `--security` / `--review` / `--refactor` / `--add-endless-test`
- Task-step plan (knowledge only) or build (code + tests) under orchestrate
- Multi-lane endless review with fix under orchestrate review (`--fix --all --endless` forced) or explicit `--review`

## When not to use

| Need | Use instead |
|------|-------------|
| Cascade planning (exec-summary → PRD) | **rr-planner** |
| PR/MR create, pipeline debug, forge POST (incl. mid-slice **ship** handoff target) | **rr-ci** |
| Local git only (rebase, worktree, squash) | **rr-git** (not plan-stage / feature-mode branch ensure) |
| Docs humanization | **rr-humanize** |

See [refs/anti-overlap.md](refs/anti-overlap.md).

## Procedure

TodoWrite `merge: false` with ids `resolve`, `mode`, `load`, `execute` when the run spans 3+ steps; omit for a single unambiguous handoff.

**Task agents:**

| Cell | Behavior |
|------|----------|
| **Isolated step run** (`drive: auto` ∧ `scope: task\|slice`, orchestrate only) | Parent spawns one sequential `generalPurpose` Task per remaining task-step. Inject: [refs/executors/step.md](refs/executors/step.md) + [refs/templates/step-task.template.md](refs/templates/step-task.template.md) + Caller Load (required / stable hard-links / variant) from the executor. Stage contracts live in [refs/slice-pipeline.md](refs/slice-pipeline.md). Parent owns ship + **pr-validate** when tip pushed; executor stops at step-validate forge landing (`ok` ≠ CI green). |
| Handoffs / `--auto --step` / `--manual` / `--feature` | Nested skills are path-loaded `Read`s only (parent-inline). |
| Nested exceptions | `--add-endless-test` → **rr-test-endless** owns `Task` dispatch to `agents/test-endless/*` per `skills/rr-builder/rr-test-endless/refs/orchestration.md`; `--refactor` → **rr-refactor** may `Task` `refactor-collector` when >50 files per `skills/rr-builder/rr-refactor/refs/agent-index.md` (fix stays inline). Inside a step executor, those same leaf Tasks stay allowed — the executor **is** the parent session for nested lanes. |

**Delivery channels:** Prefer **AskUserQuestion** (Claude) / AskQuestion (Cursor) for missing kernel/`slice_id`/feature intent, ambiguous mode, manual confirm/ready-pick, feature-mode origin probe, plan-stage feature-branch probe (not on `main`/`master`), and irreversible forks. Text-mode: same options as prose; do not stall waiting for a widget.

1. **resolve** — Load [refs/input-resolution.md](refs/input-resolution.md). Normalize flags / NL into `payload.mode` (`orchestrate` \| `feature` \| `handoff`), `payload.drive` / `payload.scope` (orchestrate defaults: `auto` × `step`; feature: `auto` × forced `task`), optional `payload.lane` / `payload.feature`, and slice/task cursor fields. Explicit lane → omit/ignore drive/scope. Done: payload emitted or one AskQuestion.
2. **mode** — If `--feature` → **feature**. Else if explicit lane flag → **handoff**. Else → **orchestrate** (probe cursor per [refs/slice-pipeline.md](refs/slice-pipeline.md)). Explicit flag wins over cursor. Done: exactly one mode.
3. **load** — Follow [refs/routing.md](refs/routing.md):
   - **Feature:** `Read` [refs/feature.md](refs/feature.md), then stage contracts from [refs/slice-pipeline.md](refs/slice-pipeline.md) with `scope=task`.
   - **Handoff:** `Read` only the matching nested `SKILL.md` once.
   - **Orchestrate:** load stage contract from [refs/slice-pipeline.md](refs/slice-pipeline.md) (full nested skill, plan allowlist, or validate rubric). Do not preload every nested skill. When Isolated step run applies and cursor is inside a task-step, load the step executor + template (do not preload every stage skill into the parent).
4. **execute** — Per mode:
   - **Feature:** detect/mint/branch per [refs/feature.md](refs/feature.md), then the drive×scope loop with hard stop at task-validate (**parent-inline** — not Isolated step run).
   - **Orchestrate:** apply the drive×scope run loop from [refs/slice-pipeline.md](refs/slice-pipeline.md). Under Isolated step run: parent **prepare** if needed → spawn step Task → **dirty-tree gate** → parent **ship** on `needs_ship` → parent **pr-validate** when tip pushed → parent **task-validate** / **slice-validate**. Manual gates use AskQuestion (+ Delivery channels fallback). Persist `builder_stage` / `step_index` / step done markers after each done-when.
   - **Handoff:** run only the nested skill loaded in step 3; no drive/scope chaining.
   - **Stop:** handoff does not re-enter orchestrate; feature does not enter slice-validate/delivered; plan stage must not edit application source (feature-branch create/checkout is allowed — [refs/feature-branch.md](refs/feature-branch.md)). Ship / validate / forge-landing / pr-validate / last-step stop rules are SoT-owned by [refs/slice-pipeline.md](refs/slice-pipeline.md) (Scope stop boundaries), [refs/ship.md](refs/ship.md), [refs/task-validate.md](refs/task-validate.md) (Forge landing), and [refs/pr-validate.md](refs/pr-validate.md) — do not re-derive them here; route planned **ship** → [refs/ship.md](refs/ship.md) then **rr-ci**, post-landing CI → [refs/pr-validate.md](refs/pr-validate.md), and **delivered** → residual **rr-ci** only. Review `--ci` handoff may `Read` `skills/rr-ci/SKILL.md` after findings.

## Nested skills (path-loaded only)

Lane → path mapping SoT: [refs/routing.md](refs/routing.md) **Handoff load table** (carries each lane's stop notes). Seven nested skills — rr-prepare, rr-coder, rr-tester, rr-security-auditor, rr-review, rr-refactor, rr-test-endless — are path-loaded `Read`s only and are not listed in `plugin.json` (README Constraints).

**Path pattern:** `skills/rr-builder/<lane>/SKILL.md` (e.g. `skills/rr-builder/rr-coder/SKILL.md`) — nested **under this skill's own folder**, never a sibling `skills/<lane>/` at the plugin's top level. Any bare `<lane>/SKILL.md` or `<lane>/refs/...` reference anywhere in this pack (routing.md, slice-pipeline.md, executors/, input-resolution.md) resolves against `skills/rr-builder/`, not against `skills/`. A "does this nested skill exist" check must stat `skills/rr-builder/<lane>/`, not `skills/<lane>/` — do not report a lane missing from a top-level `skills/` listing alone.

Nested skills set `disable-model-invocation: true` and `user-invocable: false`.

## Shared refs

| Ref | When |
|-----|------|
| [refs/input-resolution.md](refs/input-resolution.md) | Every invocation |
| [refs/routing.md](refs/routing.md) | After resolve (feature + handoff table + orchestrate pointers) |
| [refs/feature.md](refs/feature.md) | `--feature` / ad-hoc feature mode |
| [refs/slice-pipeline.md](refs/slice-pipeline.md) | Orchestrate + feature run loop (stage contracts, cursor, **Isolated step run**; feature stops at task-validate) |
| [refs/executors/step.md](refs/executors/step.md) | Isolated step run Task executor (Caller Load) |
| [refs/templates/step-task.template.md](refs/templates/step-task.template.md) | Spawn prompt for step executor |
| [refs/plan-knowledge.md](refs/plan-knowledge.md) | Orchestrate **plan** stage only |
| [refs/feature-branch.md](refs/feature-branch.md) | Plan-stage feature branch name + ensure (via plan-knowledge) |
| [refs/plan-schema.md](refs/plan-schema.md) | Orchestrate **plan** done-when / output shape (incl. **Ship**) |
| [refs/ship.md](refs/ship.md) | Orchestrate **ship** stage (branch/base resolve → rr-ci) |
| [refs/task-validate.md](refs/task-validate.md) | Task / step validate stages |
| [refs/pr-validate.md](refs/pr-validate.md) | Post forge-landing **pr-validate** (CI wait/fix via rr-ci) |
| [refs/slice-validate.md](refs/slice-validate.md) | Slice validate stage |
| [refs/anti-overlap.md](refs/anti-overlap.md) | Boundary disputes |

Missing or unreadable required ref (any Read above, or a nested skill's own required refs) → **stop** with a one-line reason; do not invent procedure or contract content from memory. If a companion ref under this pack owns the same contract, Read it and note the substitution in one line; otherwise stop.
