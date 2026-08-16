---
name: rr-planner
description: Flag-driven software planning docs — progressive top-down discovery (exec-summary → MRD → BRD → PRD → FRD), compose, research, and challenge. Use when producing exec-summary → FRD planning docs, resuming a checkpoint, or researching/challenging existing ones. Orchestrates phase agents under agents/planning/*; no command files.
---

# rr-planner

**Human overview:** [README.md](README.md)

## Purpose

Produce cascade planning docs (exec-summary → FRD) from flags and conversation. This skill owns question loops and routing. Compose, research, and challenge run as non-interactive `Task` agents under `agents/planning/*`.

## When to use

- Discover a product or plan (`--discover` / `--all`, or a cascade level flag)
- Resume a paused session (`--resume`)
- Research or challenge **existing** planning docs

## When not to use

- Implementation, code review, or ticket writing that is not cascade planning
- Inventing docs to run research or challenge — those actions require existing docs ([input-resolution.md](refs/input-resolution.md))
- Skipping parent cascade levels — expansion is owned by [input-resolution.md](refs/input-resolution.md)

## Procedure

TodoWrite `merge: false` before step 1 with stable ids `resolve`, `posture`, `level-<n>` (one per `payload.cascade_levels` entry), `compose`, `stage-exit`, `write`. Mark `completed` before advancing. Re-add `compose` and `stage-exit` with `merge: true` when entering the next level. Omit `posture` / `level-*` / `compose` / `stage-exit` when `action` is `research` or `challenge`.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Normalize raw flags and NL into `NormalizedPayload`. Done: payload emitted. Stop: that ref's deterministic errors.

Branch on `payload.action`. Do not run the sibling primary path.

| `payload.action` | Next | Todos after `resolve` |
|------------------|------|------------------------|
| `discover`, `exec-summary`…`frd` | step 2, then step 4 | `posture`, `level-*`, `compose`, `stage-exit`, `write` |
| `research`, `challenge` | step 3 (completes `write`) | `write` only |

If `payload.chain` includes `research` and/or `challenge` after a discover write, run step 3 for those phases (docs now exist). Do not start a second discover pass.

2. **discover** — Load [project-posture.md](refs/project-posture.md). Done: that ref's persist condition. Then for each level in `payload.cascade_levels`, execute [cascade.md](refs/cascade.md). Mark `level-<n>` on entry, `compose` after the compose `Task` (doc already on disk), `stage-exit` after Gate 6 freeze. Done: last listed level frozen. Stop/pause: cascade.md.

3. **research / challenge** — Load [contracts.md](refs/contracts.md). Research also loads [research-method.md](refs/research-method.md); challenge also loads [blind-spots.md](refs/blind-spots.md). `Task` the matching agent. Persist the report per [output-formats.md](refs/output-formats.md); that persist completes `write`. Done: report written. Stop: input-resolution deterministic errors; contracts parsing policy.

4. **write** (discover only, after last freeze) — Apply [success-criteria.md](refs/success-criteria.md), then pre-save reflection ([proactivity.md](refs/proactivity.md)), then persist `session-state.json` per [output-formats.md](refs/output-formats.md). Cascade docs and `items.json` are already on disk from compose. Done: session-state written. Stop: contracts parsing policy.

Load remaining refs on demand from **Shared refs**.

## Interaction boundary

Discovery runs **inline** (no discover agent) so question loops stay interactive. Compose/research/challenge `Task` agents are non-interactive; this skill asks and re-invokes ([contracts.md](refs/contracts.md)). Compose persists `{level}.md|yaml` + `items.json` and returns a slim receipt — never copy a document body through chat. Research/challenge still return findings JSON; this skill writes those reports.

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| [cascade.md](refs/cascade.md) | Start of any `--discover` run |
| [project-posture.md](refs/project-posture.md) | Discover start (pre-cascade); resume per that ref |
| [note-sessions.md](refs/note-sessions.md) | After every Q&A (classify owner); on level entry (load sidecar) |
| [doc-standards/item-schema.md](refs/doc-standards/item-schema.md) | Discovering/composing any level (IDs, split, spec/build) |
| `refs/doc-standards/<level>.md` | Discovering/composing that level only |
| [goal-anchor.md](refs/goal-anchor.md) | Entire discovery pass (always-on) |
| [proactivity.md](refs/proactivity.md) | Reflect/explore trigger during discovery; PRD cut-pass after MoSCoW; **and** pre-save reflection after last freeze (files already on disk) |
| [blind-spots.md](refs/blind-spots.md) | Stage-exit (this level's row) **and** `--challenge` (union) |
| [research-method.md](refs/research-method.md) | Research phase only |
| [output-formats.md](refs/output-formats.md) | After compose; skill write of session-state / raw-history / notes; first Q&A |
| [success-criteria.md](refs/success-criteria.md) | Pre-freeze/accept gate |
| [contracts.md](refs/contracts.md) | Before any subagent `Task` call |

Phase-specific execution steps stay in `agents/planning/*` — skill does not duplicate agent execution steps.

## Agent delegation

Invoke via `Task` with `PhaseInput` per [contracts.md](refs/contracts.md). Parse per that ref's parsing policy.

| Agent | Path | Contract |
|-------|------|----------|
| compose | `agents/planning/compose.md` | [contracts § compose](refs/contracts.md) |
| research | `agents/planning/research.md` | [contracts § research](refs/contracts.md) |
| challenge | `agents/planning/challenge.md` | [contracts § challenge](refs/contracts.md) |
