---
name: s-test-endless
description: /s-test-endless — coverage-first endless test perfection loop (default 5 epochs).
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Task, AskUserQuestion, TodoWrite
---

# s-test-endless

**Human overview:** [README.md](README.md)

## Purpose

Iterate toward stronger tests: coverage-informed assess → planner work-packs → workers → verify → re-assess. Orchestrator stays in the **invoking session** (depth 0). **`PLUGIN_ROOT`** = installed **rrraw** plugin root.

## When to use

- **`rr-builder --add-endless-test`** handoff (parent sets `lane: add_endless_test`)
- Multi-epoch coverage + heuristic perfection on repo or path scope

## When not to use

| Need | Use instead |
|------|-------------|
| One-off test assess/write | **s-tester** `--tester` |
| MR test-review fix | **s-review** `--test --fix` |

## Procedure

**Conflict resolution:** if this file and **`refs/orchestration.md`** disagree on loop mechanics, **`orchestration.md`** wins.

**Ref fallback:** If a **Load table** path fails to **Read**, stop with **`Stopped:`** per **`refs/terminal-report.md`** (reason **`policy`**) — cite the missing path. Do not invent constraints from memory. **`refs/orchestration-core.md`** § Shared load list defines required files; optional phase bundles load per **`Start:`** and loop § (see that ref).

**Delivery channels:** When **`refs/input-resolution.md`** or phase refs use **AskQuestion** / **AskUserQuestion**, offer the same options as numbered prose when the tool is unavailable — do not stall.

TodoWrite **`merge: false`** after **`Scope:`** / **`Start:`** resolve (stable ids: preflight, gateway, loop, report). During the loop, **`merge: true`** per epoch; exactly one **`in_progress`**.

1. **resolve** — Read [refs/input-resolution.md](refs/input-resolution.md) (parent should have normalized `payload.endless_test`). Mint **`runId`** per [refs/artifacts.md](refs/artifacts.md). Set **`REVIEW_ID`**, **`REVIEW_DIR`**, **`Scope:`**, **`Start:`**, **`--max-epochs`**, **`--max-parallel`**. Done: envelope ready or **Stopped:**.

2. **gateway** — **Before** first full **Read** of `orchestration.md` when iteration **`n === 1`**: **`Task`** **`test-endless-toolchain`** with prompt from [refs/toolchain-coverage-gateway-prompt.md](refs/toolchain-coverage-gateway-prompt.md) (`build` + `test:coverage`). Hard fail → **Report** **`Stopped:`**. Done: gateway pass or usable coverage per that ref.

3. **orchestrate** — **`Read`** [refs/orchestration-core.md](refs/orchestration-core.md) then [refs/orchestration.md](refs/orchestration.md). Execute loop honoring **`Start:`** entry slice. **Task** for every leaf step — no Shell-only pipeline substitute. §3b manifest = markdown in **main chat**. Done: terminal block per [refs/terminal-report.md](refs/terminal-report.md).

## Task discipline (mandatory)

Delegation, terminal shapes, and forbidden nested orchestrator rules live in **`refs/orchestration.md`** § Delegation discipline and **`refs/terminal-report.md`** — do not duplicate here.

## Load table

| Ref | When |
|-----|------|
| [refs/input-resolution.md](refs/input-resolution.md) | Resolve flags / scope / start |
| [refs/orchestration-core.md](refs/orchestration-core.md) | Before loop (core + phase bundles) |
| [refs/orchestration.md](refs/orchestration.md) | Loop index + phase routing |
| [refs/phases/coverage.md](refs/phases/coverage.md) | §0 coverage gateway (`n > 1`) |
| [refs/phases/assess.md](refs/phases/assess.md) | §1 assess, §2 exit, §8 re-assess |
| [refs/phases/plan.md](refs/phases/plan.md) | §3 plan, §3a packing gate, §3b manifest |
| [refs/phases/execute.md](refs/phases/execute.md) | §4 queue, §5 progress, §6 dispatch |
| [refs/phases/verify.md](refs/phases/verify.md) | §7 verify, §9 budget exit |
| [refs/agent-index.md](refs/agent-index.md) | Task dispatch |
| [refs/artifacts.md](refs/artifacts.md) | Paths + checkpoint schema SoT |
| [refs/leaf-contract.md](refs/leaf-contract.md) | Task envelopes |
| [refs/prompts.md](refs/prompts.md) | Assess / plan / execute bodies |
| [refs/exit-conditions.md](refs/exit-conditions.md) | Exit checks |
| [refs/terminal-report.md](refs/terminal-report.md) | Final output |
| `skills/s-review/refs/chunking.md` | Chunk list |
| `skills/s-tester/refs/shared-heuristics.md` | Cross-lane calibration (assess) |
| `skills/s-tester/refs/coverage-exclusions.md` | Non-testable taxonomy (assess) |

## Helper CLI (plugin root)

From **`PLUGIN_ROOT`**, run deterministic orchestration helpers (stdout for branching; see `scripts/endless_test_helpers/README.md`):

| Invoke | Phase |
|--------|-------|
| `python3 scripts/endless_test_helpers/cli.py packing-probes --plans-dir <dir>` | §3a |
| `python3 scripts/endless_test_helpers/cli.py dispatch-queue --plans-dir <dir> [--max-parallel N]` | §4 |
| `python3 scripts/endless_test_helpers/cli.py aggregate-counts --assess <path>...` | §1 / §2 / `Start:plan` |
| `python3 scripts/endless_test_helpers/cli.py manifest-table --plans-dir <dir> --iteration <n>` | §3b |
