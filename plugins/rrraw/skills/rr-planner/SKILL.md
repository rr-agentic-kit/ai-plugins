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
- Starting Plan without frozen BRD + `business-case.yaml` (see Entry gate)

## Entry gate

Refuse Plan compose/change/freeze-slice unless:

1. `brd` ∈ discovery `session_state.frozen_levels` (or `docs/discovery/status.yaml` frozen BRD rev), **and**
2. `docs/discovery/business-case.yaml` present with required fields (`skills/rr-discovery/refs/business-case-handoff.md`)

Exception: documented brownfield migration (legacy shallow ES+PRD) — one AskQuestion, not silent. Missing handoff → point user to `rr-discovery` freeze.

## Procedure

TodoWrite `merge: false` before step 1 with stable ids: `resolve` → `setup?` → `entry-gate` → `posture` → `standing` → `interview` → `score-architect` → `requirements` → `select` → `ac-smell` → `tech-challenge?` → `slice-freeze` → `compose`/`humanize` as needed → `write`. Mark `completed` before advancing. Omit Plan-body todos when `action` is `research` or `challenge` (only `resolve` → challenge/research → `write`). When `action` is `setup`: only `resolve`, `setup`. When `action` is `freeze-slice` with selection already done: `resolve` → `entry-gate` → `ac-smell` → `tech-challenge?` → `slice-freeze` → `write`.

Phrases: `refs/planning/progress.md` on every invocation.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Prefer `--prd` / `--change` / `--freeze-slice` / `--research` / `--challenge` / `--setup` / `--resume`. Discover flags/NL → stop and route to `rr-discovery`. Sprint/capacity/velocity → refuse and reframe as slice selection. Status-first: `docs/rrr-status.yaml` then `docs/plan/status.yaml` + session-state; entry gate also reads discovery detail. Rewrite/sync via `refs/planning/setup.md` / `refs/planning/agent-config.md`. Done: payload emitted.

| `payload.action` | Next | Todos after `resolve` |
|------------------|------|------------------------|
| `setup` | step 2 (completes `write`). Stop. | `setup` |
| `prd`, `change` | step 3 → Plan body → write | `entry-gate` through `write` as listed above |
| `freeze-slice` | step 3 → ac-smell → challenge? → slice-freeze → write | as listed |
| `research`, `challenge` | step 5 (completes `write`) | `write` only |

2. **setup** — Load `refs/planning/setup.md`. Run `sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT>`. Completes `write`. Do not start Plan compose. Default `output_dir` = `docs/plan/`.

3. **entry-gate** — Enforce Entry gate above. On fail → AskQuestion (migrate brownfield | run `rr-discovery` | abort). Do not silent-compose.

4. **Plan body** — Load [cascade.md](refs/cascade.md). In order:
   - **posture** — [project-posture.md](refs/project-posture.md) (PRD-shape, `arch_doc_mode`); offer Coach/Fast once ([plan-interview.md](refs/plan-interview.md)).
   - **standing** — [architecture.md](refs/doc-standards/architecture.md) / [constitution.md](refs/doc-standards/constitution.md); deltas via [adr-lite.md](refs/adr-lite.md) + [feature-delta.md](refs/doc-standards/feature-delta.md).
   - **interview** — [plan-interview.md](refs/plan-interview.md); notes before questions; one question/cycle default.
   - **score-architect** — [prioritization-lens.md](refs/prioritization-lens.md) + [system-design.md](refs/system-design.md). **Hard stop:** no feature Effort without architecture this pass.
   - **requirements** — full set with P1–P3 ([prd.md](refs/doc-standards/prd.md)); never shrink for build-now.
   - **select** — `_status_:` on leaves (`deferred` \| `selected` \| …).
   - **ac-smell** — WWAS + [req-smell.md](refs/req-smell.md); fail freeze without hold.
   - **tech-challenge?** — when requested or `depth: deep`: `Task` challenge; **inject** [challenge-method.md](refs/challenge-method.md); parent keeps compact `parent_summary` only (`refs/planning/contracts.md`).
   - **slice-freeze** — [execute-handoff.md](refs/execute-handoff.md); mint `execute-slice.yaml`; stamp `status.yaml` `slice:`. Draft architecture allowed.
   - **compose / humanize** — as needed: compose `Task` (`doc_type: prd` only) → mandatory compose-prose. Whole-PRD freeze = optional structure lock only.

5. **research / challenge** — Load `refs/planning/contracts.md`. Research: [research-method.md](refs/research-method.md). Challenge: [blind-spots.md](refs/blind-spots.md) + Plan [challenge-method.md](refs/challenge-method.md) + `refs/planning/decision-ledger.md`; inject Plan challenge-method into challenge `Task` (Discover stems → Discover challenge-method). Persist reports per `refs/planning/output-formats.md`. Completes `write`.

6. **write** — Apply `refs/planning/success-criteria.md`, pre-save ([proactivity.md](refs/proactivity.md)), persist `session-state.json` + `docs/plan/status.yaml` + refresh `rrr-status.yaml`. First compose: emit `docs/agent.plan.md` + sync root SoT. Done: session-state + statuses written.

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| `refs/planning/progress.md` | Every invocation |
| `refs/planning/setup.md` / `refs/planning/baselines.md` / `refs/planning/agent-config.md` | Setup, freeze, sync |
| [cascade.md](refs/cascade.md) / [project-posture.md](refs/project-posture.md) | Plan body |
| [plan-interview.md](refs/plan-interview.md) / [prioritization-lens.md](refs/prioritization-lens.md) / [system-design.md](refs/system-design.md) | Interview + score |
| [doc-standards/prd.md](refs/doc-standards/prd.md) / architecture / constitution / feature-delta | Compose standing + PRD |
| [req-smell.md](refs/req-smell.md) / [execute-handoff.md](refs/execute-handoff.md) | Pre-freeze / slice freeze |
| [challenge-method.md](refs/challenge-method.md) / [blind-spots.md](refs/blind-spots.md) | Challenge / stage-exit |
| `skills/rr-discovery/refs/compose-prose.md` | Every cascade `.md` persist |
| `skills/rr-discovery/refs/business-case-handoff.md` | Entry gate |
| `refs/planning/contracts.md` | Before any `Task` |
| Shared package | plugin `refs/planning/` (link there directly — no skill stubs) |

## Agent delegation

| Agent | Path | Contract |
|-------|------|----------|
| compose | `agents/planning/compose.md` | `refs/planning/contracts.md` — allowlist `prd` |
| research | `agents/planning/research.md` | `refs/planning/contracts.md` |
| challenge | `agents/planning/challenge.md` | `refs/planning/contracts.md` + Plan [challenge-method.md](refs/challenge-method.md) inject; compact `parent_summary` |
