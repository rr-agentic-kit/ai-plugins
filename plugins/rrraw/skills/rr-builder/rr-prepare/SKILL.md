---
name: rr-prepare
description: Decompose pin-complete execute-slice.yaml into ordered docs/rr/tasks artifacts. Use via rr-builder --prepare or prepare-slice NL.
disable-model-invocation: true
user-invocable: false
---

# rr-prepare

**Human overview:** [README.md](README.md)

## Purpose

Turn a pin-complete `execute-slice.yaml` into buildable task artifacts under `docs/rr/tasks/` so a later builder run can execute each task without inventing PRD intent, stack/mechanism, or tech law. Tracks and **lazy-writes** tech ADRs. Does **not** implement code.

## When to use

- `--prepare`, “prepare slice”, “decompose execute-slice”, or “tech plan for slice” via **rr-builder**
- After Plan slice freeze when Execute needs ordered capability atoms + PR map

## When not to use

| Need | Use instead |
|------|-------------|
| Product PRD / constitution / DEC / UX-shape | **rr-planner** |
| Implement / refactor application source | **rr-coder** |
| Open PR/MR or pipeline debug | **rr-ci** |

## Shared refs

| Ref | When |
|-----|------|
| [refs/input-resolution.md](refs/input-resolution.md) | Every invoke — resolve kernel + posture |
| [refs/tech-decisions.md](refs/tech-decisions.md) | Tech-decision gate; mint/revise `ADR-n` only when forced |
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

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Load kernel (explicit path or next open). Read pinned deltas, constitution INDEX, cited ADRs, AC refs. Classify **posture** per [sequencing.md](refs/sequencing.md). Missing freeze → stop / **rr-planner**. Done: kernel + posture stated.
2. **tech** — Inventory technical decision *topics* per [tech-decisions.md](refs/tech-decisions.md). List `pending_tech` on summary; **persist `ADR-n` only when L1/L2 would otherwise invent mechanism**. AskQuestion only for irreversible forks. Done: pending list and/or forced ADRs written.
3. **l1** — Decompose capabilities into ordered capability atoms ([task-grain.md](refs/task-grain.md), [phase-l1.md](refs/phase-l1.md)). Allocate global ids via `docs/rr/tasks/registry.yaml`. Write `task-summary.md` ([summary-template.md](refs/summary-template.md)). **Pause** for L1 validation (AskQuestion or text-mode). Done: validated ordered summary or stop on reject.
4. **l2** — One task at a time in dependency order ([phase-l2l3.md](refs/phase-l2l3.md)): research; write `{NNNN}.md` ([task-template.md](refs/task-template.md)); pass [compatibility-gate.md](refs/compatibility-gate.md); mark summary `detailed`. Default pause after each L2. Done: all L1 tasks detailed or stop on gate fail.
5. **l3** — PR division into summary + frontmatter `pr_group` ([pr-division.md](refs/pr-division.md)). Mark prepare `complete`. **Stop** — do not chain **rr-coder**.

## Nested agents (future)

No `agents/` this pass. Run L1 and L2+L3 **in the parent session** using [phase-l1.md](refs/phase-l1.md) / [phase-l2l3.md](refs/phase-l2l3.md) inject/load contracts so a later Task extraction is mechanical. N/A for live Task spawn today.
