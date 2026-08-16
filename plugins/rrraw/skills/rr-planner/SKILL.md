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
- Artifact-type advice (skill vs command, process checklist) that is not a product to plan
- Inventing docs to run research or challenge — those actions require existing docs ([input-resolution.md](refs/input-resolution.md))
- Inventing a skip of parent cascade levels — level flags expand ancestors; `depth: shallow` is the only trim ([input-resolution.md](refs/input-resolution.md))

Code/ticket work and artifact-type advice stop at resolve via `OUT_OF_SCOPE` unless a primary flag is present ([input-resolution.md](refs/input-resolution.md)).

## Procedure

TodoWrite `merge: false` before step 1 with stable ids `resolve`, `posture`, `premise`, `level-<n>` (one per `payload.cascade_levels` entry), `sweep`, `compose`, `stage-exit`, `verdict`, `write`. Mark `completed` before advancing. Re-add `sweep`, `compose`, `stage-exit`, and `verdict` with `merge: true` when entering the next level. Omit `posture` / `premise` / `level-*` / `sweep` / `compose` / `stage-exit` / `verdict` when `action` is `research` or `challenge`.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Normalize raw flags and NL into `NormalizedPayload`. If `output_dir` (or a cascade `--input` dir) already has cascade docs, run `python3 scripts/validate_planning.py --rewrite <dir>` before any `Task`. Done: payload emitted; stale md/yaml rewritten. Stop: that ref's deterministic errors.

Branch on `payload.action`. Do not run the sibling primary path.

| `payload.action` | Next | Todos after `resolve` |
|------------------|------|------------------------|
| `discover`, `exec-summary`…`frd` | step 2, then step 4 | `posture`, `premise`, `level-*`, `sweep`, `compose`, `stage-exit`, `verdict`, `write` |
| `research`, `challenge` | step 3 (completes `write`) | `write` only |

If `payload.chain` includes `research` and/or `challenge`, run step 3 after step 2 (last level frozen; docs on disk) and before step 4. Do not start a second discover pass.

2. **discover** — Load [project-posture.md](refs/project-posture.md) (includes `domain_context`). Done: that ref's persist condition. Then for each level in `payload.cascade_levels`, execute [cascade.md](refs/cascade.md). Mark `level-<n>` on entry, `sweep` after the re-decision sweep, `premise` after the exec-summary premise test (skip the id on later levels), `compose` after the compose `Task`, `stage-exit` after Gate 6, `verdict` after Gate 7. Done: last listed level frozen. Stop/pause: cascade.md.

3. **research / challenge** — Load [contracts.md](refs/contracts.md). Research also loads [research-method.md](refs/research-method.md); challenge also loads [blind-spots.md](refs/blind-spots.md) and [decision-ledger.md](refs/decision-ledger.md). `Task` the matching agent. Research: agent returns when its iteration budget is exhausted (`ok`, or `partial` + `clarifications_needed`); skill may re-`Task` or stop when the user confirms done. Persist the report per [output-formats.md](refs/output-formats.md); that persist completes `write`. Done: report written. Stop: input-resolution deterministic errors; contracts parsing policy.

4. **write** (discover only, after last freeze and any `payload.chain` phases) — Apply [success-criteria.md](refs/success-criteria.md), then pre-save reflection ([proactivity.md](refs/proactivity.md)), then persist `session-state.json` per [output-formats.md](refs/output-formats.md). Done: session-state written. Stop: contracts parsing policy.

Load remaining refs on demand from **Shared refs**.

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| [cascade.md](refs/cascade.md) | Discover-path actions (`discover` or a cascade level flag) |
| [project-posture.md](refs/project-posture.md) | Discover start (pre-cascade); resume per that ref; PRD cut-pass after MoSCoW |
| [note-sessions.md](refs/note-sessions.md) | After every Q&A; on level entry; after compose persist |
| [doc-standards/item-schema.md](refs/doc-standards/item-schema.md) | Discovering/composing any level |
| `refs/doc-standards/<level>.md` | Discovering/composing that level only |
| [goal-anchor.md](refs/goal-anchor.md) | Entire discovery pass (always-on); reason-graph is **not** this ref |
| [expert-panel.md](refs/expert-panel.md) | ES premise test; Gate 7; evidence loop; `--resume` when viability/queue is open |
| [decision-ledger.md](refs/decision-ledger.md) | Rationale mint; every sweep trigger; compose reads `reserved_ids`; challenge scan |
| [proactivity.md](refs/proactivity.md) | Reflect/explore trigger during discovery; pre-save after last freeze |
| [blind-spots.md](refs/blind-spots.md) | Stage-exit (this level's row); `--challenge` (union) |
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
