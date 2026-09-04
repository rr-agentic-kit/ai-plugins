---
name: rr-planner
description: Flag-driven Plan — PRD+ from frozen business-case. Use after Discover freeze; setup/research/challenge PRD. Problem/market work → rr-discovery.
---

# rr-planner

**Human overview:** [README.md](README.md)

## Purpose

Produce **PRD+** from a **frozen business case**. Discover (executive-summary → MRD → BRD + `business-case.yaml`) is owned by `rr-discovery`. This skill owns Plan Q&A and routing. Compose, research, and challenge run as non-interactive `Task` agents under `agents/planning/*`. Cascade prose persists only after [compose-prose.md](../rr-discovery/refs/compose-prose.md) → `rr-humanize`.

## When to use

- Bootstrap or repair the docs framework (`--setup`) — does not start discover
- Compose or change PRD (`--prd`, `--change` with `--section` + `--target`) after Discover freeze
- Resume a paused Plan session (`--resume`)
- Research or challenge **existing** Plan docs (typically PRD)

## When not to use

- Problem, market, viability, ideation, GTM framing, or BRD work → `rr-discovery`
- Implementation, code review, or ticket writing that is not cascade planning
- Inventing docs to run research or challenge — those actions require existing docs ([input-resolution.md](refs/input-resolution.md))
- Starting Plan without frozen BRD + `business-case.yaml` (see Entry gate)

## Entry gate

Refuse Plan compose/change on PRD unless:

1. `brd` ∈ discovery `session_state.frozen_levels` (or `docs/discovery/status.yaml` frozen BRD rev), **and**
2. `docs/discovery/business-case.yaml` present with required fields ([business-case-handoff.md](../rr-discovery/refs/business-case-handoff.md))

Exception: documented brownfield migration (legacy shallow ES+PRD) — one AskQuestion, not silent. Missing handoff → point user to `rr-discovery` freeze.

## Procedure

TodoWrite `merge: false` before step 1 with stable ids `resolve`, `entry-gate`, `level-prd`, `sweep`, `compose`, `humanize`, `stage-exit`, `write`. Omit level todos when `action` is `research` or `challenge`. When `action` is `setup`: only `resolve`, `setup`.

Phrases: [progress.md](../../../refs/planning/progress.md) on every invocation.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Prefer `--prd` / `--change` / `--research` / `--challenge` / `--setup` / `--resume`. If flags request Discover stems (`--discover`, `--executive-summary`, `--mrd`, `--brd`) without Plan intent → stop and route to `rr-discovery`. Status-first: `docs/rrr-status.yaml` then `docs/plan/status.yaml` + session-state; entry gate also reads discovery detail. Rewrite/sync via [setup.md](../../../refs/planning/setup.md) / [agent-config.md](../../../refs/planning/agent-config.md). Done: payload emitted.

| `payload.action` | Next | Todos after `resolve` |
|------------------|------|------------------------|
| `setup` | step 2 (completes `write`). Stop. | `setup` |
| `prd`, `change` | step 3 (entry gate) → step 4 → step 6 | `entry-gate`, `level-prd`, `sweep`, `compose`, `humanize`, `stage-exit`, `write` |
| `research`, `challenge` | step 5 (completes `write`) | `write` only |

2. **setup** — Load [setup.md](../../../refs/planning/setup.md). Run `sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT>`. Completes `write`. Do not start Plan compose. Default `output_dir` = `docs/plan/`.

3. **entry-gate** — Enforce Entry gate above. On fail → AskQuestion (migrate brownfield | run `rr-discovery` | abort). Do not silent-compose PRD.

4. **plan (PRD)** — Load [doc-standards/prd.md](refs/doc-standards/prd.md), [project-posture.md](refs/project-posture.md) (PRD-shape reflection), [cascade.md](refs/cascade.md). Sweep → compose `Task` (`doc_type: prd` only) → **mandatory** [compose-prose.md](../rr-discovery/refs/compose-prose.md) → Gate 3 / stage-exit (PRD blind-spot row) → freeze PRD per [baselines.md](../../../refs/planning/baselines.md); refresh summary (`phase: plan|complete`).

5. **research / challenge** — Load [contracts.md](../../../refs/planning/contracts.md). Research: [research-method.md](refs/research-method.md). Challenge: [blind-spots.md](refs/blind-spots.md) + [decision-ledger.md](../../../refs/planning/decision-ledger.md); inject method ref into challenge `Task` (PRD taxonomy; Discover stems → prefer [challenge-method.md](../rr-discovery/refs/challenge-method.md) unless user insists). Persist reports per [output-formats.md](../../../refs/planning/output-formats.md). Completes `write`.

6. **write** — Apply [success-criteria.md](../../../refs/planning/success-criteria.md), persist `session-state.json` + `docs/plan/status.yaml` + refresh `rrr-status.yaml`. First compose: emit `docs/agent.plan.md` + sync root SoT. Done: session-state + statuses written.

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| [progress.md](../../../refs/planning/progress.md) | Every invocation |
| [setup.md](../../../refs/planning/setup.md) / [baselines.md](../../../refs/planning/baselines.md) / [agent-config.md](../../../refs/planning/agent-config.md) | Setup, freeze, sync |
| [doc-standards/prd.md](refs/doc-standards/prd.md) | PRD compose |
| [compose-prose.md](../rr-discovery/refs/compose-prose.md) | Every cascade `.md` persist |
| [business-case-handoff.md](../rr-discovery/refs/business-case-handoff.md) | Entry gate |
| [research-method.md](refs/research-method.md) | Research |
| [blind-spots.md](refs/blind-spots.md) | Challenge / PRD stage-exit |
| [contracts.md](../../../refs/planning/contracts.md) | Before any `Task` |
| Shared package | plugin `refs/planning/` (link there directly — no skill stubs) |

## Agent delegation

| Agent | Path | Contract |
|-------|------|----------|
| compose | `agents/planning/compose.md` | [contracts § compose](../../../refs/planning/contracts.md) — allowlist `prd` |
| research | `agents/planning/research.md` | [contracts § research](../../../refs/planning/contracts.md) |
| challenge | `agents/planning/challenge.md` | [contracts § challenge](../../../refs/planning/contracts.md) |
