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
| `review` | `rr-review/SKILL.md` | Nested `--code|--test|--security|--all|--fix|--ci` per `rr-review/refs/params.md` |

After review `--ci` findings: **Read** `skills/rr-ci/SKILL.md` for forge POST. Do not open PR from other lanes.

Local worktree / destructive git during review `--fix`: **Read** `skills/rr-git/refs/` as rr-review already directs — does not replace standalone **rr-git**.

## Orchestrate stage → load table

Load table below is unchanged by drive/scope. Run loop (auto/manual × next/full, readiness) lives in [slice-pipeline.md](slice-pipeline.md). Validate rubrics: [task-validate.md](task-validate.md), [slice-validate.md](slice-validate.md).

| Stage | Load | Execute application source? |
|-------|------|------------------------------|
| **prepare** | Full `rr-prepare/SKILL.md` | No |
| **plan** | **Knowledge only** — rr-coder Required Knowledge (incl. [architecture.md](../rr-coder/refs/architecture.md) when AR-relevant) + rr-tester refs needed for step assessment (heuristics/contracts). Do **not** follow full implement Procedures | **No** |
| **build** | Full `rr-coder/SKILL.md` **and** `rr-tester/SKILL.md` (code + tests for the step) | **Yes** |
| **review** | Full `rr-review/SKILL.md` with forced `--fix --all` | Via review fix path |
| **refactor** | TBD stub — skip or stop `refactor stage not specified` | No invented procedure |
| **step_validate** / **task_validate** | [task-validate.md](task-validate.md) | No |
| **slice_validate** | [slice-validate.md](slice-validate.md) | No |
| **delivered** | Stop — point to **rr-ci** | No |

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
- Auto-chaining prepare → build without cursor/done-when.
- Running **rr-ci** / opening PR from **slice delivered** (builder stops; engineer invokes **rr-ci**).
- Using **rr-builder** for exec-summary / PRD authoring → **rr-planner**.
- Inventing a **refactor** stage procedure while TBD.
