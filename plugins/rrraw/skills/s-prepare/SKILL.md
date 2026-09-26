---
name: s-prepare
description: /s-prepare — decompose a pin-complete execute-slice into docs/rr/tasks; also via rr-builder --prepare or orchestrate prepare.
disable-model-invocation: true
---

# s-prepare

**Human overview:** [README.md](README.md)

## Purpose

Turn a pin-complete `execute-slice.yaml` into buildable task artifacts under `docs/rr/tasks/` so a later builder run can execute each task without inventing PRD intent, stack/mechanism, or tech law. Tracks and **lazy-writes** tech ADRs. Does **not** implement code.

## When to use

- `--prepare`, “prepare slice”, “decompose execute-slice”, or “tech plan for slice” via **rr-builder** (explicit handoff)
- Also loaded under **rr-builder** orchestration when the pipeline cursor is still in **prepare** (drive/scope per parent)
- After Plan slice freeze when Execute needs ordered capability atoms + PR map

## When not to use

| Need | Use instead |
|------|-------------|
| Product PRD / constitution / DEC / UX-shape | **rr-planner** |
| Implement / refactor application source | **s-coder** |
| Open PR/MR or pipeline debug | **s-ci** |

## Shared refs

| Ref | When |
|-----|------|
| [refs/input-resolution.md](refs/input-resolution.md) | Every invoke — resolve kernel + posture |
| [refs/tech-decisions.md](refs/tech-decisions.md) | Tech-decision gate; lazy ADR |
| [refs/sequencing.md](refs/sequencing.md) | L1 `depends_on` + L2 reorder checks |
| [refs/task-grain.md](refs/task-grain.md) | L1 atom sizing |
| [refs/summary-template.md](refs/summary-template.md) | Write / update `task-summary.md` |
| [refs/phase-l1.md](refs/phase-l1.md) | L1 inject/load contract |
| [refs/task-template.md](refs/task-template.md) | Write each `{NNNN}.md` |
| [refs/compatibility-gate.md](refs/compatibility-gate.md) | L2 done-when before marking `detailed` |
| [refs/pr-division.md](refs/pr-division.md) | L3 PR map |
| [refs/phase-l2l3.md](refs/phase-l2l3.md) | L2+L3 inject/load contract |

Missing required ref → **stop** with one-line reason; do not invent procedure from memory.

## Procedure

TodoWrite `merge: false` with ids `resolve`, `tech`, `l1`, `l2`, `l3` when the run spans 3+ steps.

**Delivery channels:** Prefer AskQuestion for load-bearing irreversible forks and L1 validation. Text-mode: same options as prose; do not stall waiting for a widget.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Load kernel (explicit path preferred; pathless → one `kernel_path` or stop). Read pinned deltas, constitution INDEX, cited ADRs, AC refs. Classify **posture** token per [sequencing.md](refs/sequencing.md). Missing freeze → stop / **rr-planner**. Done: session payload emitted (`kernel_path`, `slice_id`, `track`, `posture`, `pins`, `pending_tech`) per input-resolution Output.
2. **tech** — Inventory topics and apply mint rules per [tech-decisions.md](refs/tech-decisions.md). List `pending_tech` on summary. AskQuestion only for irreversible forks. Done: pending list and/or forced ADRs written.
3. **l1** — Decompose capabilities into ordered capability atoms ([task-grain.md](refs/task-grain.md), [phase-l1.md](refs/phase-l1.md)). Allocate global ids via [task-template.md](refs/task-template.md) Id allocation (stdout→value). Write `task-summary.md` ([summary-template.md](refs/summary-template.md)). Run [sequencing.md](refs/sequencing.md) Cycle probe. **Pause** for L1 validation (AskQuestion or text-mode) — pass only if: Cycle probe PASS; every row grain-PASS; every row has `requirement_ids` or an explicit prep unlock; posture token noted on summary. Done: validated ordered summary or stop on reject.
4. **l2** — Detail tasks in dependency order ([phase-l2l3.md](refs/phase-l2l3.md)): research; write `{NNNN}.md` ([task-template.md](refs/task-template.md)); pass [compatibility-gate.md](refs/compatibility-gate.md); mark summary `detailed`. **Default: batch** remaining outlined tasks (`batch_l2: true`). Pause after each L2 only when parent sets `batch_l2: false` / `pause_each_l2`. Compatibility-gate still runs per task before `detailed`. Done: all L1 tasks detailed or stop on gate fail.
5. **l3** — PR division into summary + frontmatter `pr_group` ([pr-division.md](refs/pr-division.md)). Done when: every detailed task has `pr_group`; summary PR map written; `prepare_status: complete`. **Stop** — do not chain **s-coder**.

## Nested agents (future)

No `agents/` this pass. Run L1 and L2+L3 **in the parent session** using [phase-l1.md](refs/phase-l1.md) / [phase-l2l3.md](refs/phase-l2l3.md) inject/load contracts so a later Task extraction is mechanical. N/A for live Task spawn today.
