---
name: rr-discovery
description: Flag-driven Discover — ES→MRD→BRD freeze to business-case; --from-code from source. Before PRD; setup/resume/challenge. Not Plan (rr-planner).
---

# rr-discovery

**Human overview:** [README.md](README.md)

## Purpose

Prove a product (venture or internal) exists before naming Plan capabilities. Owns discovery Q&A, cascade through BRD, reverse-from-code compose, and the frozen `business-case.yaml` handoff. Compose and challenge run as non-interactive `Task` agents under `agents/planning/*`. Cascade prose persists only after [compose-prose.md](refs/compose-prose.md) → `rr-humanize`.

## When to use

- Bootstrap or repair the docs framework (`--setup`) — does not start discover
- Discover a product or bet (`--discover` / `--all`, or `--executive-summary` / `--mrd` / `--brd`)
- Reverse Discover stems from an existing codebase (`--from-code`) — research + compose → `maturity: code-extraction`; not interview-driven
- Change a frozen discovery track (`--change` with `--section` + `--target` on ES/MRD/BRD)
- Resume a paused discovery session (`--resume`) — promote `code-extraction` → `draft` when continue-shaping
- Challenge **existing** ES/MRD/BRD docs (`--challenge` + [challenge-method.md](refs/challenge-method.md))

## When not to use

- PRD compose, RICE/stories, research reports, feature backlog → `rr-planner`
- Implementation, code review, tickets, launch calendars, analytics/CI (except `--from-code` when intent is Discover docs from source)
- Architecture / `tech.md` mechanism authorship as Discover deliverable
- Jumping to features before freeze — park via [note-sessions.md](refs/note-sessions.md)

## Procedure

TodoWrite `merge: false` before step 1 with stable ids `resolve`, `posture`, `ideation`, `premise`, `level-<n>` (one per `payload.cascade_levels` entry), `sweep`, `compose`, `humanize`, `stage-exit`, `verdict`, `freeze-handoff`, `write`. When `action` is `from-code`: use `resolve`, `posture`, `from-code`, `level-<n>`, `sweep`, `compose`, `humanize`, `write` — **omit** `ideation` and **omit** `freeze-handoff` while any stem is `maturity: code-extraction`. Mark `completed` before advancing. Re-add `sweep`, `compose`, `humanize`, `stage-exit`, and `verdict` with `merge: true` when entering the next level. Omit discovery level todos when `action` is `challenge`. When `action` is `setup`: only `resolve`, `setup`.

Phrases: `refs/planning/progress.md` on every invocation.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Accept legacy `--exec-summary` → `executive-summary`. No `--prd` / `--research` as primary. Status-first: read `docs/rr/rrr-status.yaml` then `docs/rr/{track}/discovery/status.yaml` + session-state. If cascade docs exist, rewrite via `sh scripts/validate_planning.sh --rewrite <dir>`. Sync agent config via `refs/planning/agent-config.md`. Done: payload emitted. Stop: that ref's deterministic errors.

| `payload.action` | Next | Todos after `resolve` |
|------------------|------|------------------------|
| `setup` | step 2 (completes `write`). Stop. | `setup` |
| `discover`, `executive-summary`…`brd`, `change` | step 3 → step 5 → step 6 | posture through write |
| `from-code` | step 3a → step 6 (no freeze-handoff) | posture, from-code, levels, compose, humanize, write |
| `challenge` | step 4 (completes `write`) | `write` only |

If `payload.chain` includes `challenge`, run step 4 after last freeze and before step 6.

2. **setup** — Load `refs/planning/setup.md`. Run `sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT>`. Completes `write`. Do not start discover. Default `output_dir` = `docs/rr/{track}/discovery/`.

3. **discover** — Load [project-posture.md](refs/project-posture.md) (includes `domain_context`). Done: that ref's persist condition.
   - **Ideation gate** — If problem space without concrete idea → load [ideation.md](refs/ideation.md) before L1 compose; else skip. Persist OST/assumptions/pretotype when produced (humanize session artifacts via [compose-prose.md](refs/compose-prose.md)). **Skip entirely when `action` is `from-code`.**
   - For each level in `payload.cascade_levels`, execute [cascade.md](refs/cascade.md). Mark `level-<n>` on entry, `sweep` after re-decision sweep, `premise` after ES premise test (skip on later levels), `compose` after compose `Task`, `humanize` after [compose-prose.md](refs/compose-prose.md), `stage-exit` after Gate 6, `verdict` after Gate 7.
   - After compose draft: **mandatory** [compose-prose.md](refs/compose-prose.md) before treating persist complete.
   - On-demand: [interview-method.md](refs/interview-method.md), [strategy-lenses.md](refs/strategy-lenses.md), [gtm-framing.md](refs/gtm-framing.md).
   - Done: last listed level frozen. After BRD freeze → step 5. **Not for `from-code`** — see 3a.

3a. **from-code** — Load [from-code.md](refs/from-code.md) after posture. Research codebase (`--input` root or `PROJECT_ROOT`); persist `from_code_evidence`; compose stems with `maturity: code-extraction`; ask **contradictions only**; stop without freeze. On later `--resume` / continue-shaping that edits toward normal Discover: promote maturity → `draft`, then enter step 3 discover chain (gates/freeze as interview-sourced).

4. **challenge** — Load `refs/planning/contracts.md`, [challenge-method.md](refs/challenge-method.md), [blind-spots.md](refs/blind-spots.md), `refs/planning/decision-ledger.md`. `Task` challenge agent for **exactly one** ES/MRD/BRD stem; **inject** `challenge-method.md` path into the Task prompt. Persist `{stem}.challenge.report.md` (humanize prose body). Stamp `docs/rr/{track}/discovery/status.yaml` challenge per `refs/planning/baselines.md`. Completes `write`.

5. **freeze-handoff** (after BRD Gates 1–7) — Load [business-case-handoff.md](refs/business-case-handoff.md). **Refuse** while any stem is `maturity: code-extraction`. Mint freeze, write `business-case.yaml`, stamp detail + summary (`discovery_complete`, `phase`, `summary` line), require conditional artifacts if techniques ran. Fail freeze on missing required fields or decorative metrics. **Next Up:** Plan (`rr-planner`).

6. **write** — Apply `refs/planning/success-criteria.md`, pre-save ([proactivity.md](refs/proactivity.md)), persist `session-state.json` + phase `status.yaml` + refresh `rrr-status.yaml` per `refs/planning/output-formats.md`. Done: session-state + statuses written.

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| `refs/planning/progress.md` | Every invocation |
| `refs/planning/setup.md` | `action: setup`; resolve rewrite/sync |
| `refs/planning/baselines.md` | **Version law** — resolve; freeze; challenge stamp; open-next; ship |
| [cascade.md](refs/cascade.md) | Discover-path actions |
| [project-posture.md](refs/project-posture.md) | Discover / from-code start |
| [from-code.md](refs/from-code.md) | `action: from-code` |
| [ideation.md](refs/ideation.md) | Ideation gate / assumptions / pretotype (not from-code) |
| [compose-prose.md](refs/compose-prose.md) | Every cascade `.md` persist |
| `refs/planning/project-lexicon.md` | After compose-prose / from-code research persist |
| [business-case-handoff.md](refs/business-case-handoff.md) | BRD freeze → Plan handoff |
| `refs/doc-standards/<level>.md` | Composing that level |
| [goal-anchor.md](refs/goal-anchor.md) / [expert-panel.md](refs/expert-panel.md) | Discovery pass / Gate 7 |
| [note-sessions.md](refs/note-sessions.md) | After every Q&A; level entry |
| [challenge-method.md](refs/challenge-method.md) | `--challenge` / `depth: deep` |
| `refs/planning/contracts.md` | Before any subagent `Task` |

Shared planning package: plugin `refs/planning/` (link there directly — no skill stubs). Versioning SoT is `refs/planning/baselines.md` only — do not copy into this skill tree. Future Execute loads the same file.

## Agent delegation

| Agent | Path | Contract |
|-------|------|----------|
| compose | `agents/planning/compose.md` | `refs/planning/contracts.md` § compose — allowlist `executive-summary`\|`mrd`\|`brd` |
| challenge | `agents/planning/challenge.md` | `refs/planning/contracts.md` § challenge + [challenge-method.md](refs/challenge-method.md) |

Compose does **not** own humanize — skill runs [compose-prose.md](refs/compose-prose.md) after draft receipt.
