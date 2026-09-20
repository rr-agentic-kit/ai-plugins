# rr-builder routing

**Audience:** `rr-builder` after [input-resolution.md](input-resolution.md).

## Handoff load table

Exact one nested `SKILL.md` **Read**. Stop at that skill’s done-when. Do **not** re-enter orchestration or advance `builder_stage` past the handoff lane.

| `payload.lane` | Load | Notes |
|----------------|------|-------|
| `prepare` | `rr-prepare/SKILL.md` | Stop after L3; no auto-chain to coder |
| `coder` | `rr-coder/SKILL.md` | Implement/refactor only for scoped request |
| `tester` | `rr-tester/SKILL.md` | Forward test payload; parent does not re-parse conflicts |
| `security` | `rr-security-auditor/SKILL.md` | Report-only |
| `review` | `rr-review/SKILL.md` | Nested `--code|--test|--security|--all|--fix|--ci|--endless` per `rr-review/refs/params.md` |
| `refactor` | `rr-refactor/SKILL.md` | Fixed-point behavior-invariant refactor; `Task` `refactor-collector` only when >50 files per `rr-refactor/refs/agent-index.md` |
| `add_endless_test` | `rr-test-endless/SKILL.md` | Coverage-first multi-epoch loop; `Task` for gateway + leaf agents per `rr-test-endless/refs/orchestration.md` |

After review `--ci` findings: **Read** `skills/rr-ci/SKILL.md` for forge POST. Do not open PR from other lanes.

Local worktree / destructive git during review `--fix`: **Read** `skills/rr-git/refs/` as rr-review already directs — does not replace standalone **rr-git**.

## Orchestrate stage → load

**SoT for stage contracts, Loads, execute-source?, and done-when:** [slice-pipeline.md](slice-pipeline.md) (Task-step stage contracts + Knowledge load vs full-skill). Do **not** maintain a parallel Loads matrix here.

| Stage | Pointer |
|-------|---------|
| **prepare** | Full `rr-prepare/SKILL.md` |
| **plan** | [plan-knowledge.md](plan-knowledge.md) + [plan-schema.md](plan-schema.md) |
| **build** | Full `rr-coder/SKILL.md` **and** `rr-tester/SKILL.md` |
| **refactor** | Full `rr-refactor/SKILL.md` — scope = MR ∩ **build-touched** paths; see [slice-pipeline.md](slice-pipeline.md) |
| **review** | Full `rr-review/SKILL.md` with forced `--fix --all --endless` |
| **step_validate** / **task_validate** | [task-validate.md](task-validate.md) |
| **ship** | [ship.md](ship.md) then `skills/rr-ci/SKILL.md` |
| **slice_validate** | [slice-validate.md](slice-validate.md) |
| **delivered** | Stop — point to **rr-ci** for residual unshipped work |

Run loop (auto/manual × next/step/task/slice, readiness, cursor): [slice-pipeline.md](slice-pipeline.md).

### Review lane delegation (inside rr-review)

When `rr-review` runs assess:

| Lane | Nested skill |
|------|--------------|
| `code` | `rr-coder/SKILL.md` |
| `test` | `rr-tester/SKILL.md` |
| `security` | `rr-security-auditor/SKILL.md` |

Review orchestration (brief, chunk, Challenge, merge report) stays in **rr-review**; lane rubrics stay in nested skills.

## Anti-patterns

- Loading all nested `SKILL.md` files in one turn (preload-all).
- Re-entering **orchestrate** after an explicit handoff in the same run.
- Writing application source during **plan** stage.
- Dumping rr-coder Required Knowledge / language matrices on **plan** (use [plan-knowledge.md](plan-knowledge.md) only).
- Inventing plan/build/refactor/review/ship completion from prose — use `step_*_done` fields ([slice-pipeline.md](slice-pipeline.md)).
- Auto-chaining prepare → build without cursor/done-when.
- Opening PR/MR inside builder without **rr-ci** (including mid-slice **ship** — hand off, do not invent forge CLI).
- Emitting shippable **step-validate** / **task-validate** PASS without an open PR for `Ship.branch`.
- Requiring Forge/PR when `ship_after: never` was confirmed (non-shippable).
- Skipping planned **ship** when shippable validate fails the Forge/PR gate (`ship_after` is not `never`).
- Shipping only *after* validate PASS when the forge gate is what blocks PASS (wrong order).
- Using **rr-builder** for exec-summary / PRD authoring → **rr-planner**.
- **`Task`** for refactor fix worker (fix is inline only per `rr-refactor/refs/inline-fix.md`).
