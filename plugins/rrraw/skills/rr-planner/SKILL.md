---
name: rr-planner
description: Flag-driven Plan — goal-likelihood for Discover OMTM via honest Effort + slice kernel. After Discover freeze; setup/challenge/freeze-slice. Market→rr-discovery.
---

# rr-planner

**Human overview:** [README.md](README.md)

## Purpose

Produce a **trustworthy Plan** from a **frozen business case**: dual-lens sitting yields **honest RICE Effort** (cost drivers in constitution/delta — tech and/or UX) and a **buildable slice kernel** (`execute-slice.yaml`) so future Execute starts fused code+test without inventing stack, mechanism, or cost-driving UX shape. Artifacts include full feature requirement sets, scored backlog, standing constitution (+ tech ADRs on demand), per-feature deltas, WWAS AC, and compact freeze. **Success** = raises the odds the builder reaches the frozen Discover objective / OMTM — Effort honesty + pin-complete kernel are **necessary preconditions**, not the finish line. Freeze only when further Plan work stops moving that likelihood **and** no open standing red flag / Discover-reopen blocks it — **not** product-doc section coverage or smell-clean ceremony. Discover (ES→MRD→BRD + `business-case.yaml`) is owned by `rr-discovery`. This skill owns Plan Q&A and routing. Compose, research, and challenge run as non-interactive `Task` agents under `agents/planning/*`. Cascade prose persists only after `skills/rr-discovery/refs/compose-prose.md` → `rr-humanize`. Ambient context-budget hooks (Cursor + Claude) inject soft/hard attention when the plugin is installed — [context-budget.md](refs/context-budget.md).

## When to use

- Bootstrap or repair the docs framework (`--setup`) — does not start Plan
- Compose or change PRD / standing Plan docs (`--prd`, `--change`) after Discover freeze
- Select requirements and freeze a slice (`--freeze-slice` / NL)
- Resume a paused Plan session (`--resume`)
- Research or challenge **existing** Plan docs (PRD, constitution, deltas, AC)
- Optimize oversized Plan docs (`--optimize`) — suggest → AskQuestion → apply

## When not to use

- Problem, market, viability, ideation, GTM framing, or BRD work → `rr-discovery`
- Traditional sprint / capacity / velocity ceremony → refuse; reframe as slice selection
- Release/version bundling of slices → deferred; do not invent those artifacts this pass
- Implementation, Execute, ship-check, code review, or ticket writing that is not cascade planning → **rr-builder**
- Artifact-type advice (skill vs command, process checklist) that is not a product to plan
- Inventing docs to run research or challenge — those actions require existing docs ([input-resolution.md](refs/input-resolution.md))
- Starting Plan without frozen BRD + `business-case.yaml` — [input-resolution.md](refs/input-resolution.md) Entry gate

## Procedure

TodoWrite `merge: false` before step 1 with stable ids matching [cascade.md](refs/cascade.md) Happy path (Plan): `resolve` → `setup?` → `entry-gate` → `posture` → `standing` → `dual-lens` → `requirements` → `compose` → `humanize` → `select` → `exit-gates` → `tech-challenge` → `slice-freeze` → `write`. Mark `completed` before advancing. Omit Plan-body todos when `action` is `research` or `challenge` (only `resolve` → detect → research/challenge → `write`). When `action` is `setup`: only `resolve`, `setup`. When `action` is `optimize`: `resolve` → optimize loop → `write`. When `action` is `freeze-slice` with selection already done: `resolve` → `entry-gate` → `exit-gates` → `tech-challenge?` → `slice-freeze` → `write`.

Phrases: `refs/planning/progress.md` on every invocation.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Prefer `--prd` / `--change` / `--freeze-slice` / `--research` / `--challenge` / `--optimize` / `--setup` / `--resume`. Discover flags/NL → stop and route to `rr-discovery`. Sprint/capacity/velocity → refuse and reframe as slice selection. Status-first: `docs/rr/rrr-status.yaml` then `docs/rr/{track}/plan/status.yaml` + **session-state via** `sh scripts/session_state.sh view --path {output_dir}/session-state.json` (never full-file `Read`). Entry gate also reads discovery detail. Rewrite/sync via `refs/planning/setup.md` / `refs/planning/agent-config.md`. Done: payload emitted; resume/status-first tool output includes a session-state projection.

| `payload.action` | Next | Todos after `resolve` |
|------------------|------|------------------------|
| `setup` | step 2 (completes `write`). Stop. | `setup` |
| `prd`, `change` | step 3 → Plan body → write | Happy path: `entry-gate` through `write` |
| `freeze-slice` | step 3 → truncated freeze path → write | `entry-gate` → `exit-gates` → `tech-challenge?` → `slice-freeze` → `write` |
| `optimize` | step 5b (completes `write`) | `write` only |
| `research`, `challenge` | step 5 (completes `write`) | `write` only |

2. **setup** — Load `refs/planning/setup.md`. Run `sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT>`. Completes `write`. Do not start Plan compose. Default `output_dir` = `docs/rr/{track}/plan/`.

3. **entry-gate** — Enforce [input-resolution.md](refs/input-resolution.md) Entry gate. On fail → AskQuestion (migrate brownfield | run `rr-discovery` | abort). Do not silent-compose.

4. **Plan body** — Load [cascade.md](refs/cascade.md) Happy path / Side paths; for `prd` / `change` / `freeze-slice` run phases in that order (truncated per Side paths). Before marking any phase todo `completed`, run [goal-anchor.md](refs/goal-anchor.md) **Standing self-challenge** (auto-reflection — `refs/planning/challenge-layers.md`). Invariants only: dual-lens same sitting; humanize-before-select order per cascade; scoped load per [context-budget.md](refs/context-budget.md); freeze bar per [execute-handoff.md](refs/execute-handoff.md). Done: cascade Advancing vs stopping or pause checkpoint.

5. **research / challenge** — Load `refs/planning/contracts.md`. Pre-Task: context-budget detect per [context-budget.md](refs/context-budget.md). Research: obey [research-method.md](refs/research-method.md). Challenge: obey Plan [challenge-method.md](refs/challenge-method.md) + [blind-spots.md](refs/blind-spots.md) + `refs/planning/decision-ledger.md` + `refs/planning/challenge-layers.md` (inject challenge-method into challenge `Task`; Discover stems → Discover challenge-method). Completes `write`.

5b. **optimize** — Load [context-budget.md](refs/context-budget.md) `--optimize` procedure. Completes `write`.

6. **write** — Apply `refs/planning/success-criteria.md`, pre-save ([proactivity.md](refs/proactivity.md)), persist `session-state.json` **via** `scripts/session_state.sh` mutators + `docs/rr/{track}/plan/status.yaml` + refresh `rrr-status.yaml`. Multi-doc absorb → **batch** parallel mutators / compose `Task` (do not serial-invent across many files). First compose: emit `docs/rr/agent.plan.md` + sync root SoT. Next Up / freeze-suggest: `refs/planning/progress.md` + `refs/planning/challenge-layers.md`. Done: session-state + statuses written (no full-file checkpoint `Read`).

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| `refs/planning/progress.md` | Every invocation |
| `refs/planning/challenge-layers.md` | Challenge / freeze-suggest / auto-reflection |
| `refs/planning/setup.md` / `refs/planning/baselines.md` / `refs/planning/agent-config.md` | Setup; **version law** (freeze / open-next / ship); sync |
| [cascade.md](refs/cascade.md) / [project-posture.md](refs/project-posture.md) | Plan body |
| [plan-interview.md](refs/plan-interview.md) / [prioritization-lens.md](refs/prioritization-lens.md) / [system-design.md](refs/system-design.md) | `dual-lens` (same sitting) |
| [nature-expectation-packs.md](refs/nature-expectation-packs.md) | Interview / nature reflection (reflect → derive → elicit; not a pack fire-table) |
| [doc-standards/prd.md](refs/doc-standards/prd.md) / constitution / architecture / feature-delta | Compose standing + PRD |
| [decision-lite.md](refs/decision-lite.md) | Co-load with feature-delta / architecture / standing shards |
| [context-budget.md](refs/context-budget.md) | After standing; pre research/challenge Task; `--optimize`; plugin hooks; scoped-load SoT |
| [req-smell.md](refs/req-smell.md) / [execute-handoff.md](refs/execute-handoff.md) | Pre-freeze / slice freeze (freeze bar SoT = execute-handoff) |
| [challenge-method.md](refs/challenge-method.md) / [blind-spots.md](refs/blind-spots.md) | Challenge / stage-exit |
| [research-method.md](refs/research-method.md) | Research action |
| [proactivity.md](refs/proactivity.md) | Pre-save / write |
| [goal-anchor.md](refs/goal-anchor.md) / [expert-panel.md](refs/expert-panel.md) | Plan pass / Gate 2; Gate 7 / resume viability |
| [note-sessions.md](refs/note-sessions.md) | After every Q&A; Plan level entry |
| [domain-routing.md](refs/domain-routing.md) | Challenge / blind-spot domain placement; access-axis placement |
| `skills/rr-discovery/refs/compose-prose.md` | Every cascade `.md` persist |
| `refs/planning/project-lexicon.md` | After compose-prose (lexicon harvest) |
| `skills/rr-discovery/refs/business-case-handoff.md` | Entry gate |
| `refs/planning/contracts.md` | Before any `Task` |
| `scripts/session_state.README.md` | resolve / resume / write session-state (run CLI; do not load `.py`) |
| Shared package | plugin `refs/planning/` (link there directly — no skill stubs). Versioning SoT: `refs/planning/baselines.md` only — future Execute loads the same file. |

No matching technique ref → stop + AskQuestion; do not invent procedure.

## Agent delegation

| Agent | Path | Contract |
|-------|------|----------|
| compose | `agents/planning/compose.md` | `refs/planning/contracts.md` — allowlist `prd` |
| research | `agents/planning/research.md` | `refs/planning/contracts.md` |
| challenge | `agents/planning/challenge.md` | `refs/planning/contracts.md` + Plan [challenge-method.md](refs/challenge-method.md) inject; compact `parent_summary` |

Compose does **not** own humanize — skill runs `skills/rr-discovery/refs/compose-prose.md` after draft receipt.
