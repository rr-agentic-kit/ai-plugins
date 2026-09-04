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

TodoWrite `merge: false` before step 1 with stable ids `resolve`, `posture`, `ideation`, `premise`, `level-<n>` (one per `payload.cascade_levels` entry), `sweep`, `compose`, `humanize`, `stage-exit`, `verdict`, `freeze-handoff`, `write`. Mark `completed` before advancing. Re-add `sweep`, `compose`, `humanize`, `stage-exit`, and `verdict` with `merge: true` when entering the next level. Omit discovery level todos when `action` is `challenge`. When `action` is `setup`: only `resolve`, `setup`.

Phrases: [progress.md](../../../refs/planning/progress.md) on every invocation.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Accept legacy `--exec-summary` → `executive-summary`. No `--prd` / `--research` as primary. Status-first: read `docs/rrr-status.yaml` then `docs/discovery/status.yaml` + session-state. If cascade docs exist, rewrite via `sh scripts/validate_planning.sh --rewrite <dir>`. Sync agent config via [agent-config.md](../../../refs/planning/agent-config.md). Done: payload emitted. Stop: that ref's deterministic errors.

| `payload.action` | Next | Todos after `resolve` |
|------------------|------|------------------------|
| `setup` | step 2 (completes `write`). Stop. | `setup` |
| `discover`, `executive-summary`…`brd`, `change` | step 3 → step 5 → step 6 | posture through write |
| `challenge` | step 4 (completes `write`) | `write` only |

If `payload.chain` includes `challenge`, run step 4 after last freeze and before step 6.

2. **setup** — Load [setup.md](../../../refs/planning/setup.md). Run `sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT>`. Completes `write`. Do not start discover. Default `output_dir` = `docs/discovery/`.

3. **discover** — Load [project-posture.md](refs/project-posture.md) (includes `domain_context`). Done: that ref's persist condition.
   - **Ideation gate** — If problem space without concrete idea → load [ideation.md](refs/ideation.md) before L1 compose; else skip. Persist OST/assumptions/pretotype when produced (humanize session artifacts via [compose-prose.md](refs/compose-prose.md)).
   - For each level in `payload.cascade_levels`, execute [cascade.md](refs/cascade.md). Mark `level-<n>` on entry, `sweep` after re-decision sweep, `premise` after ES premise test (skip on later levels), `compose` after compose `Task`, `humanize` after [compose-prose.md](refs/compose-prose.md), `stage-exit` after Gate 6, `verdict` after Gate 7.
   - After compose draft: **mandatory** [compose-prose.md](refs/compose-prose.md) before treating persist complete.
   - On-demand: [interview-method.md](refs/interview-method.md), [strategy-lenses.md](refs/strategy-lenses.md), [gtm-framing.md](refs/gtm-framing.md).
   - Done: last listed level frozen. After BRD freeze → step 5.

4. **challenge** — Load [contracts.md](../../../refs/planning/contracts.md), [challenge-method.md](refs/challenge-method.md), [blind-spots.md](refs/blind-spots.md), [decision-ledger.md](../../../refs/planning/decision-ledger.md). `Task` challenge agent for **exactly one** ES/MRD/BRD stem; **inject** `challenge-method.md` path into the Task prompt. Persist `{stem}.challenge.report.md` (humanize prose body). Stamp `docs/discovery/status.yaml` challenge per [baselines.md](../../../refs/planning/baselines.md). Completes `write`.

5. **freeze-handoff** (after BRD Gates 1–7) — Load [business-case-handoff.md](refs/business-case-handoff.md). Mint freeze, write `business-case.yaml`, stamp detail + summary (`discovery_complete`, `phase`, `summary` line), require conditional artifacts if techniques ran. Fail freeze on missing required fields or decorative metrics. **Next Up:** Plan (`rr-planner`).

6. **write** — Apply [success-criteria.md](../../../refs/planning/success-criteria.md), pre-save ([proactivity.md](refs/proactivity.md)), persist `session-state.json` + phase `status.yaml` + refresh `rrr-status.yaml` per [output-formats.md](../../../refs/planning/output-formats.md). Done: session-state + statuses written.

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| [progress.md](../../../refs/planning/progress.md) | Every invocation |
| [setup.md](../../../refs/planning/setup.md) | `action: setup`; resolve rewrite/sync |
| [baselines.md](../../../refs/planning/baselines.md) | Resolve; freeze; challenge stamp |
| [cascade.md](refs/cascade.md) | Discover-path actions |
| [project-posture.md](refs/project-posture.md) | Discover start |
| [ideation.md](refs/ideation.md) | Ideation gate / assumptions / pretotype |
| [compose-prose.md](refs/compose-prose.md) | Every cascade `.md` persist |
| [business-case-handoff.md](refs/business-case-handoff.md) | BRD freeze → Plan handoff |
| `refs/doc-standards/<level>.md` | Composing that level |
| [goal-anchor.md](refs/goal-anchor.md) / [expert-panel.md](refs/expert-panel.md) | Discovery pass / Gate 7 |
| [note-sessions.md](refs/note-sessions.md) | After every Q&A; level entry |
| [challenge-method.md](refs/challenge-method.md) | `--challenge` / `depth: deep` |
| [contracts.md](../../../refs/planning/contracts.md) | Before any subagent `Task` |

Shared planning package: plugin `refs/planning/` (link there directly — no skill stubs).

## Agent delegation

| Agent | Path | Contract |
|-------|------|----------|
| compose | `agents/planning/compose.md` | [contracts § compose](../../../refs/planning/contracts.md) — allowlist `executive-summary`\|`mrd`\|`brd` |
| challenge | `agents/planning/challenge.md` | [contracts § challenge](../../../refs/planning/contracts.md) + [challenge-method.md](refs/challenge-method.md) |

Compose does **not** own humanize — skill runs [compose-prose.md](refs/compose-prose.md) after draft receipt.
