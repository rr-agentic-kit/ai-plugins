# rr-builder routing

**Audience:** `rr-builder` after [input-resolution.md](input-resolution.md).

## Feature mode

When `payload.mode: feature`:

1. **Read** [feature.md](feature.md) (detect → branch ensure → mint → cursor).
2. Enter the task run-loop from [slice-pipeline.md](slice-pipeline.md) with forced `scope=task` and durable paths under `payload.feature.artifact_root`.
3. **Hard stop** at task-validate done-when — do **not** treat as a nested-skill handoff; do **not** advance to slice-validate / delivered.

## Handoff load table

**SoT for lane → nested-SKILL.md mapping.** SKILL.md carries a one-line pointer to this table only — update this table first when lanes change. Exact one nested `SKILL.md` **Read**. Stop at that skill’s done-when. Do **not** re-enter orchestration or advance `builder_stage` past the handoff lane.

**Path pattern:** every `Load` below is nested under this skill's own folder — `skills/rr-builder/<lane>/SKILL.md` — not a sibling `skills/<lane>/`.

| `payload.lane` | Load | Notes |
|----------------|------|-------|
| `prepare` | `skills/rr-builder/rr-prepare/SKILL.md` | Stop after L3; no auto-chain to coder |
| `coder` | `skills/rr-builder/rr-coder/SKILL.md` | Implement/refactor only for scoped request |
| `tester` | `skills/rr-builder/rr-tester/SKILL.md` | Forward test payload; parent does not re-parse conflicts |
| `security` | `skills/rr-builder/rr-security-auditor/SKILL.md` | Report-only |
| `review` | `skills/rr-builder/rr-review/SKILL.md` | Nested `--code|--test|--security|--all|--fix|--ci|--endless` per `skills/rr-builder/rr-review/refs/params.md` |
| `refactor` | `skills/rr-builder/rr-refactor/SKILL.md` | Fixed-point behavior-invariant refactor; `Task` `refactor-collector` only when >50 files per `skills/rr-builder/rr-refactor/refs/agent-index.md` |
| `add_endless_test` | `skills/rr-builder/rr-test-endless/SKILL.md` | Coverage-first multi-epoch loop; `Task` for gateway + leaf agents per `skills/rr-builder/rr-test-endless/refs/orchestration.md` |

After review `--ci` findings: **Read** `skills/rr-ci/SKILL.md` for forge POST. Do not open PR from other lanes.

Local worktree / destructive git during review `--fix`: **Read** `skills/rr-git/refs/` as rr-review already directs — does not replace standalone **rr-git**.

## Orchestrate stage → load

**SoT for stage contracts, Loads, execute-source?, and done-when:** [slice-pipeline.md](slice-pipeline.md) (Task-step stage contracts + Knowledge load vs full-skill). Do **not** maintain a parallel Loads matrix here.

| Stage | Pointer |
|-------|---------|
| **prepare** | Full `skills/rr-builder/rr-prepare/SKILL.md` |
| **plan** | [plan-knowledge.md](plan-knowledge.md) + [plan-schema.md](plan-schema.md) |
| **build** | Full `skills/rr-builder/rr-coder/SKILL.md` **and** `skills/rr-builder/rr-tester/SKILL.md` |
| **refactor** | Full `skills/rr-builder/rr-refactor/SKILL.md` — scope = MR ∩ **build-touched** paths; see [slice-pipeline.md](slice-pipeline.md) |
| **review** | Full `skills/rr-builder/rr-review/SKILL.md` with forced `--fix --all --endless` |
| **step_validate** / **task_validate** | [task-validate.md](task-validate.md) |
| **ship** | [ship.md](ship.md) then `skills/rr-ci/SKILL.md` |
| **pr_validate** | [pr-validate.md](pr-validate.md) then `skills/rr-ci/SKILL.md` |
| **slice_validate** | [slice-validate.md](slice-validate.md) |
| **delivered** | Stop — point to **rr-ci** for residual unshipped work |

Run loop (auto/manual × next/step/task/slice, readiness, cursor): [slice-pipeline.md](slice-pipeline.md).

### Review lane delegation (inside rr-review)

When `rr-review` runs assess:

| Lane | Nested skill |
|------|--------------|
| `code` | `skills/rr-builder/rr-coder/SKILL.md` |
| `test` | `skills/rr-builder/rr-tester/SKILL.md` |
| `security` | `skills/rr-builder/rr-security-auditor/SKILL.md` |

Review orchestration (brief, chunk, Challenge, merge report) stays in **rr-review**; lane rubrics stay in nested skills.

## Anti-patterns

- Loading all nested `SKILL.md` files in one turn (preload-all).
- Re-entering **orchestrate** after an explicit handoff in the same run.
- Writing application source during **plan** stage.
- Dumping rr-coder Required Knowledge / language matrices on **plan** (use [plan-knowledge.md](plan-knowledge.md) only).
- Inventing plan/build/refactor/review/ship/pr-validate completion from prose — use `step_*_done` fields ([slice-pipeline.md](slice-pipeline.md)).
- Auto-chaining prepare → build without cursor/done-when.
- Opening PR/MR inside builder without **rr-ci** — boundary SoT: [anti-overlap.md](anti-overlap.md) rr-ci section.
- Emitting shippable **step-validate** / **task-validate** PASS without an open PR for `Ship.branch`.
- Advancing past shippable validate with sidecars absent from tip and no carry-to-next — rules SoT: [task-validate.md](task-validate.md) Forge landing (isolation cell: dirty porcelain is always a hard-stop).
- Advancing past a landed open tip with failing/pending CI — rules SoT: [pr-validate.md](pr-validate.md).
- Parent-inline implement of a task-step under **Isolated step run** (`auto` × `task|slice`) — spawn [executors/step.md](executors/step.md) instead ([slice-pipeline.md](slice-pipeline.md)).
- Requiring Forge/PR when `ship_after: never` was confirmed (non-shippable).
- Skipping planned **ship** when shippable validate fails the Forge/PR gate (`ship_after` is not `never`).
- Shipping only *after* validate PASS when the forge gate is what blocks PASS (wrong order).
- Serial-loading co-named plan allowlist / build nested `SKILL.md` Reads that [plan-knowledge.md](plan-knowledge.md) / [slice-pipeline.md](slice-pipeline.md) mark for one parallel turn.
- Using **rr-builder** for exec-summary / PRD authoring → **rr-planner**.
- **`Task`** for refactor fix worker (fix is inline only per `skills/rr-builder/rr-refactor/refs/inline-fix.md`).

### Nested Task (isolation cell)

Under Isolated step run, the **step executor** is the parent session for nested lane skills. Leaf Tasks those skills already document (`refactor-collector`, tester agents, rr-test-endless leaves, etc.) stay allowed. Forbidden from the step executor: re-invoke **rr-builder**; spawn sibling step Tasks; run `--add-endless-test`.
