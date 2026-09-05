---
name: rr-discovery
description: Flag-driven Discover — ES→MRD→BRD freeze to business-case. Use before PRD; setup/resume/challenge discovery stems. Not for PRD (rr-planner).
---

# rr-discovery

**Human overview:** [README.md](README.md)

## Purpose

Prove a product (venture or internal) exists before naming Plan capabilities. Owns discovery Q&A, cascade through BRD, and the frozen `business-case.yaml` handoff. Compose and challenge run as non-interactive `Task` agents under `agents/planning/*`. Cascade prose persists only after [compose-prose.md](refs/compose-prose.md) → `rr-humanize`.

## When to use

- Bootstrap or repair the docs framework (`--setup`) — does not start discover
- Discover a product or bet (`--discover` / `--all`, or `--executive-summary` / `--mrd` / `--brd`)
- Change a frozen discovery track (`--change` with `--section` + `--target` on ES/MRD/BRD)
- Resume a paused discovery session (`--resume`)
- Challenge **existing** ES/MRD/BRD docs (`--challenge` + [challenge-method.md](refs/challenge-method.md))

## When not to use

- PRD compose, RICE/stories, research reports, feature backlog → `rr-planner`
- Implementation, code review, tickets, launch calendars, analytics/CI
- Architecture / `tech.md` mechanism authorship as Discover deliverable
- Jumping to features before freeze — park via [note-sessions.md](refs/note-sessions.md)

## Procedure

TodoWrite `merge: false` before step 1 with stable ids `resolve`, `setup`, `posture`, `ideation`, `premise`, `level-<n>` (one per `payload.cascade_levels` entry), `sweep`, `compose`, `humanize`, `stage-exit`, `verdict`, `freeze-handoff`, `write`. Mark `completed` before advancing. Per level: re-add `sweep` → `compose` → `humanize` → `stage-exit` → `verdict` with `merge: true` (cascade cycle). Omit discovery level todos when `action` is `challenge`. When `action` is `setup`: only `resolve`, `setup`.

Phrases: `refs/planning/progress.md` on every invocation.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Done/Stop: that ref.

| `payload.action` | Next | Todos after `resolve` |
|------------------|------|------------------------|
| `setup` | step 2 (completes `write`). Stop. | `setup` |
| `discover`, `executive-summary`…`brd`, `change` | step 3, then chain below | posture through write |
| `challenge` | step 4 (completes `write`) | `write` only |

Chain after step 3: if `payload.chain` includes `challenge` → `3 → 4 → 5 → 6`; else → `3 → 5 → 6`.

2. **setup** — Load `refs/planning/setup.md`. Run `sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT>`. Default `output_dir` = `docs/discovery/`. Done: setup script succeeded; completes `write`. Stop: setup errors; do not start discover.

3. **discover** — Load [project-posture.md](refs/project-posture.md) (includes `domain_context`). Done: that ref's Persist condition.
   - For each level in `payload.cascade_levels`, execute [cascade.md](refs/cascade.md) (per-level cycle + gates).
   - On-demand: [interview-method.md](refs/interview-method.md), [strategy-lenses.md](refs/strategy-lenses.md), [gtm-framing.md](refs/gtm-framing.md).
   - Done: last listed level frozen. Then follow chain (step 1): challenge-in-chain → step 4; else → step 5.
   - Stop / pause ("stop", "pause", "done for now"): leave drafts on disk; checkpoint `session-state.json` (`refs/planning/output-formats.md`); set `checkpoint.status: paused` with `current_level`; skip pre-save. Resume: `--resume --output-dir <same-dir>` — load checkpoint; sweep; continue.

4. **challenge** — Load `refs/planning/contracts.md`, [challenge-method.md](refs/challenge-method.md), [blind-spots.md](refs/blind-spots.md), `refs/planning/decision-ledger.md`. `Task` challenge agent for **exactly one** ES/MRD/BRD stem; **inject** `challenge-method.md` path into the Task prompt. Persist `{stem}.challenge.report.md` (humanize prose body). Stamp `docs/discovery/status.yaml` challenge per `refs/planning/baselines.md`. Done: report + stamp written; completes `write` when challenge is primary. Stop: contracts/challenge-method errors; missing stem.

5. **freeze-handoff** (after BRD Gates 1–7) — Load [business-case-handoff.md](refs/business-case-handoff.md). Done/Stop: that ref. **Next Up:** Plan (`rr-planner`).

6. **write** — Apply `refs/planning/success-criteria.md`, pre-save ([proactivity.md](refs/proactivity.md)), persist `session-state.json` + phase `status.yaml` + refresh `rrr-status.yaml` per `refs/planning/output-formats.md`. Done: session-state + statuses written. Stop: pre-save block (open queue / binding `hold`/`kill`).

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| `refs/planning/progress.md` | Every invocation |
| `refs/planning/setup.md` | `action: setup`; resolve rewrite/sync |
| `refs/planning/baselines.md` | Resolve; freeze; challenge stamp |
| [cascade.md](refs/cascade.md) | Discover-path actions |
| [project-posture.md](refs/project-posture.md) | Discover start |
| [ideation.md](refs/ideation.md) | Ideation gate / assumptions / pretotype |
| [compose-prose.md](refs/compose-prose.md) | Every cascade `.md` persist |
| [business-case-handoff.md](refs/business-case-handoff.md) | BRD freeze → Plan handoff |
| `refs/doc-standards/<level>.md` | Composing that level |
| [goal-anchor.md](refs/goal-anchor.md) / [expert-panel.md](refs/expert-panel.md) | Discovery pass / Gate 7 |
| [domain-routing.md](refs/domain-routing.md) | Blind-spot names a domain topic |
| [note-sessions.md](refs/note-sessions.md) | After every Q&A; level entry |
| [challenge-method.md](refs/challenge-method.md) | `--challenge` / `depth: deep` |
| `refs/planning/contracts.md` | Before any subagent `Task` |

If no listed on-demand ref matches → continue with Procedure only; do not invent a ref.

Shared planning package: plugin `refs/planning/` (link there directly — no skill stubs).

## Agent delegation

| Agent | Path | Contract |
|-------|------|----------|
| compose | `agents/planning/compose.md` | `refs/planning/contracts.md` § compose — allowlist `executive-summary`\|`mrd`\|`brd` |
| challenge | `agents/planning/challenge.md` | `refs/planning/contracts.md` § challenge + [challenge-method.md](refs/challenge-method.md) |
