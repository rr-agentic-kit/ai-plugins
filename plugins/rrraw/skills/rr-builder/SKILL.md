---
name: rr-builder
description: Slice build orchestrator (drive×scope; default --auto --step) or lane handoff via --prepare/--coder/--tester/--security/--review/--refactor/--add-endless-test. Not rr-planner/rr-ci.
---

# rr-builder

**Human overview:** [README.md](README.md)

## Purpose

**Orchestrate** building a pin-complete execute-slice for software engineers: prepare → per-task plan/build/refactor/review/validate → optional planned **ship** (rr-ci handoff) → slice validate → **delivered** residual. Drive (`--auto` \| `--manual`) × scope (`--next` \| `--step` \| `--task` \| `--slice`) control confirm gates and how far one run advances. With an explicit lane flag, **hand off** to exactly one nested skill and stop (drive/scope ignored). Artifacts: `docs/rr/tasks/` (prepare/execute cursor), `.ai/review/<runId>/` (review), `.ai/refactor/<runId>/` (refactor).

## When to use

- Continue or resume a frozen slice (orchestrate: no lane flag; defaults `drive=auto`, `scope=step`)
- Run without confirms (`--auto`), only the cursor stage (`--next`), one task-step (`--step`), one task (`--task`), or until delivered (`--slice`)
- Explicit single-lane work: `--prepare` / `--coder` / `--tester` / `--security` / `--review` / `--refactor` / `--add-endless-test`
- Task-step plan (knowledge only) or build (code + tests) under orchestrate
- Multi-lane endless review with fix under orchestrate review (`--fix --all --endless` forced) or explicit `--review`

## When not to use

| Need | Use instead |
|------|-------------|
| Cascade planning (exec-summary → PRD) | **rr-planner** |
| PR/MR create, pipeline debug, forge POST (incl. mid-slice **ship** handoff target) | **rr-ci** |
| Local git only (rebase, worktree, squash) | **rr-git** (not plan-stage feature-branch ensure) |
| Docs humanization | **rr-humanize** |

See [refs/anti-overlap.md](refs/anti-overlap.md).

## Procedure

TodoWrite `merge: false` with ids `resolve`, `mode`, `load`, `execute` when the run spans 3+ steps; omit for a single unambiguous handoff.

**Task agents:** N/A for most handoffs — nested skills are path-loaded `Read`s only. **Exceptions:** `--add-endless-test` → **rr-test-endless** owns `Task` dispatch to `agents/test-endless/*` per `rr-test-endless/refs/orchestration.md`; `--refactor` → **rr-refactor** may `Task` `refactor-collector` when >50 files per `rr-refactor/refs/agent-index.md` (fix stays inline).

**Delivery channels:** Prefer AskQuestion for missing kernel/`slice_id`, ambiguous mode, manual confirm/ready-pick, plan-stage feature-branch probe (not on `main`/`master`), and irreversible forks. Text-mode: same options as prose; do not stall waiting for a widget.

1. **resolve** — Load [refs/input-resolution.md](refs/input-resolution.md). Normalize flags / NL into `payload.mode` (`orchestrate` \| `handoff`), `payload.drive` / `payload.scope` (orchestrate defaults: `auto` × `step`), optional `payload.lane`, and slice/task cursor fields. Explicit lane → omit/ignore drive/scope. Done: payload emitted or one AskQuestion.
2. **mode** — If explicit lane flag → **handoff**. Else → **orchestrate** (probe cursor per [refs/slice-pipeline.md](refs/slice-pipeline.md)). Explicit flag wins over cursor. Done: exactly one mode.
3. **load** — Follow [refs/routing.md](refs/routing.md):
   - **Handoff:** `Read` only the matching nested `SKILL.md` once.
   - **Orchestrate:** load stage contract from [refs/slice-pipeline.md](refs/slice-pipeline.md) (full nested skill, plan allowlist, or validate rubric). Do not preload every nested skill.
4. **execute** — Apply drive×scope run loop from [refs/slice-pipeline.md](refs/slice-pipeline.md). Manual gates use AskQuestion (+ Delivery channels fallback). Persist `builder_stage` / `step_index` / step done markers after each done-when. **Stop** — handoff does not re-enter orchestrate; plan stage must not edit application source (feature-branch create/checkout is allowed — [refs/feature-branch.md](refs/feature-branch.md)); planned **ship** → [refs/ship.md](refs/ship.md) then **rr-ci** (do not invent forge CLI); **delivered** → residual rr-ci only. Review `--ci` handoff may `Read` `skills/rr-ci/SKILL.md` after findings.

## Nested skills (path-loaded only)

| Lane / stage use | Path | Listed in plugin.json |
|------------------|------|------------------------|
| Prepare | [rr-prepare/SKILL.md](rr-prepare/SKILL.md) | no |
| Coder | [rr-coder/SKILL.md](rr-coder/SKILL.md) | no |
| Tester | [rr-tester/SKILL.md](rr-tester/SKILL.md) | no |
| Security | [rr-security-auditor/SKILL.md](rr-security-auditor/SKILL.md) | no |
| Review hub | [rr-review/SKILL.md](rr-review/SKILL.md) | no |
| Refactor | [rr-refactor/SKILL.md](rr-refactor/SKILL.md) | no |
| Endless add-test | [rr-test-endless/SKILL.md](rr-test-endless/SKILL.md) | no |

Nested skills set `disable-model-invocation: true` and `user-invocable: false`.

## Shared refs

| Ref | When |
|-----|------|
| [refs/input-resolution.md](refs/input-resolution.md) | Every invocation |
| [refs/routing.md](refs/routing.md) | After resolve (handoff table + orchestrate pointers) |
| [refs/slice-pipeline.md](refs/slice-pipeline.md) | Orchestrate mode (stage contracts, cursor, run loop) |
| [refs/plan-knowledge.md](refs/plan-knowledge.md) | Orchestrate **plan** stage only |
| [refs/feature-branch.md](refs/feature-branch.md) | Plan-stage feature branch name + ensure (via plan-knowledge) |
| [refs/plan-schema.md](refs/plan-schema.md) | Orchestrate **plan** done-when / output shape (incl. **Ship**) |
| [refs/ship.md](refs/ship.md) | Orchestrate **ship** stage (branch/base resolve → rr-ci) |
| [refs/task-validate.md](refs/task-validate.md) | Task / step validate stages |
| [refs/slice-validate.md](refs/slice-validate.md) | Slice validate stage |
| [refs/anti-overlap.md](refs/anti-overlap.md) | Boundary disputes |
