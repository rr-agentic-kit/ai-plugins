---
name: rr-planner
description: Flag-driven Plan — requirements, spine, slice freeze from frozen business-case. After Discover freeze; setup/challenge/freeze-slice. Market work → rr-discovery.
---

# rr-planner

**Human overview:** [README.md](README.md)

## Purpose

Produce **Plan** artifacts from a **frozen business case**: full feature requirement sets, scored backlog, standing architecture spine (+ constitution), per-feature deltas, WWAS AC, and compact slice freeze for future Execute. Discover (ES→MRD→BRD + `business-case.yaml`) is owned by `rr-discovery`. This skill owns Plan Q&A and routing. Compose, research, and challenge run as non-interactive `Task` agents under `agents/planning/*`. Cascade prose persists only after `skills/rr-discovery/refs/compose-prose.md` → `rr-humanize`.

## When to use

- Bootstrap or repair the docs framework (`--setup`) — does not start Plan
- Compose or change PRD / standing Plan docs (`--prd`, `--change`) after Discover freeze
- Select requirements and freeze a slice (`--freeze-slice` / NL)
- Resume a paused Plan session (`--resume`)
- Research or challenge **existing** Plan docs (PRD, architecture, deltas, AC)

## When not to use

- Problem, market, viability, ideation, GTM framing, or BRD work → `rr-discovery`
- Traditional sprint / capacity / velocity ceremony → refuse; reframe as slice selection
- Release/version bundling of slices → deferred; do not invent those artifacts this pass
- Implementation, Execute, ship-check, or ticket writing that is not cascade planning
- Inventing docs to run research or challenge — those actions require existing docs ([input-resolution.md](refs/input-resolution.md))
- Starting Plan without frozen BRD + `business-case.yaml` — [input-resolution.md](refs/input-resolution.md) Entry gate

## Procedure

TodoWrite `merge: false` before step 1 with stable ids: `resolve` → `setup?` → `entry-gate` → `posture` → `standing` → `interview` → `score-architect` → `requirements` → `select` → `ac-smell` → `tech-challenge?` → `slice-freeze` → `compose`/`humanize` as needed → `write`. Mark `completed` before advancing. Omit Plan-body todos when `action` is `research` or `challenge` (only `resolve` → challenge/research → `write`). When `action` is `setup`: only `resolve`, `setup`. When `action` is `freeze-slice` with selection already done: `resolve` → `entry-gate` → `ac-smell` → `tech-challenge?` → `slice-freeze` → `write`.

Phrases: `refs/planning/progress.md` on every invocation.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Prefer `--prd` / `--change` / `--freeze-slice` / `--research` / `--challenge` / `--setup` / `--resume`. Discover flags/NL → stop and route to `rr-discovery`. Sprint/capacity/velocity → refuse and reframe as slice selection. Status-first: `docs/rr/rrr-status.yaml` then `docs/rr/{track}/plan/status.yaml` + session-state; entry gate also reads discovery detail. Rewrite/sync via `refs/planning/setup.md` / `refs/planning/agent-config.md`. Done: payload emitted.

| `payload.action` | Next | Todos after `resolve` |
|------------------|------|------------------------|
| `setup` | step 2 (completes `write`). Stop. | `setup` |
| `prd`, `change` | step 3 → Plan body → write | `entry-gate` through `write` as listed above |
| `freeze-slice` | step 3 → ac-smell → challenge? → slice-freeze → write | as listed |
| `research`, `challenge` | step 5 (completes `write`) | `write` only |

2. **setup** — Load `refs/planning/setup.md`. Run `sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT>`. Completes `write`. Do not start Plan compose. Default `output_dir` = `docs/rr/{track}/plan/`.

3. **entry-gate** — Enforce [input-resolution.md](refs/input-resolution.md) Entry gate. On fail → AskQuestion (migrate brownfield | run `rr-discovery` | abort). Do not silent-compose.

4. **Plan body** — Load [cascade.md](refs/cascade.md). For `prd` / `change` / `freeze-slice`: run Pre-Plan posture → Level order → Per-level cycle as that ref directs. Mark `posture`, `standing`, `interview`, `score-architect`, `requirements`, `select`, `ac-smell`, `tech-challenge?`, `slice-freeze`, `compose`/`humanize` as cascade phases complete. Done: that ref's Advancing vs stopping conditions or pause checkpoint.

5. **research / challenge** — Load `refs/planning/contracts.md`. Research: [research-method.md](refs/research-method.md). Challenge: [blind-spots.md](refs/blind-spots.md) + Plan [challenge-method.md](refs/challenge-method.md) + `refs/planning/decision-ledger.md`; inject Plan challenge-method into challenge `Task` (Discover stems → Discover challenge-method). Persist reports per `refs/planning/output-formats.md`. Completes `write`.

6. **write** — Apply `refs/planning/success-criteria.md`, pre-save ([proactivity.md](refs/proactivity.md)), persist `session-state.json` + `docs/rr/{track}/plan/status.yaml` + refresh `rrr-status.yaml`. First compose: emit `docs/rr/agent.plan.md` + sync root SoT. Done: session-state + statuses written.

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| `refs/planning/progress.md` | Every invocation |
| `refs/planning/setup.md` / `refs/planning/baselines.md` / `refs/planning/agent-config.md` | Setup; **version law** (freeze / open-next / ship); sync |
| [cascade.md](refs/cascade.md) / [project-posture.md](refs/project-posture.md) | Plan body |
| [plan-interview.md](refs/plan-interview.md) / [prioritization-lens.md](refs/prioritization-lens.md) / [system-design.md](refs/system-design.md) | Interview + score |
| [doc-standards/prd.md](refs/doc-standards/prd.md) / architecture / constitution / feature-delta | Compose standing + PRD |
| [req-smell.md](refs/req-smell.md) / [execute-handoff.md](refs/execute-handoff.md) | Pre-freeze / slice freeze |
| [challenge-method.md](refs/challenge-method.md) / [blind-spots.md](refs/blind-spots.md) | Challenge / stage-exit |
| [goal-anchor.md](refs/goal-anchor.md) / [expert-panel.md](refs/expert-panel.md) | Plan pass / Gate 2; Gate 7 / resume viability |
| [note-sessions.md](refs/note-sessions.md) | After every Q&A; Plan level entry |
| [domain-routing.md](refs/domain-routing.md) | Challenge / blind-spot domain placement |
| `skills/rr-discovery/refs/compose-prose.md` | Every cascade `.md` persist |
| `skills/rr-discovery/refs/business-case-handoff.md` | Entry gate |
| `refs/planning/contracts.md` | Before any `Task` |
| Shared package | plugin `refs/planning/` (link there directly — no skill stubs). Versioning SoT: `refs/planning/baselines.md` only — future Execute loads the same file. |

No matching technique ref → stop + AskQuestion; do not invent procedure.

## Agent delegation

| Agent | Path | Contract |
|-------|------|----------|
| compose | `agents/planning/compose.md` | `refs/planning/contracts.md` — allowlist `prd` |
| research | `agents/planning/research.md` | `refs/planning/contracts.md` |
| challenge | `agents/planning/challenge.md` | `refs/planning/contracts.md` + Plan [challenge-method.md](refs/challenge-method.md) inject; compact `parent_summary` |

Compose does **not** own humanize — skill runs `skills/rr-discovery/refs/compose-prose.md` after draft receipt.
