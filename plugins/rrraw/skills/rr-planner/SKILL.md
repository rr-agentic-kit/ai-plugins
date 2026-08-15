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
- `--challenge` / `--research` with no docs in `--input` or `--output-dir` — hard-stop `MISSING_DOCS`; do not invent docs
- Ad-hoc child-level polish that skips parent cascade levels (`cascade_levels` expansion is owned by [input-resolution.md](refs/input-resolution.md))

## Procedure

TodoWrite `merge: false` before step 1 with stable ids `resolve`, `posture`, `level-<n>` (one per `payload.cascade_levels` entry), `compose`, `stage-exit`, `write`. Mark `completed` before advancing. Re-add `compose` and `stage-exit` with `merge: true` when entering the next level. Omit `posture` / `level-*` / `compose` / `stage-exit` when `action` is `research` or `challenge`.

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md). Normalize raw flags and NL into `NormalizedPayload`. Do not restate flag handlers; `cascade_levels` is owned there. Done: payload emitted. Stop: that ref's deterministic errors.
2. **posture** (discover / level-focus) — Load [project-posture.md](refs/project-posture.md). Classify before exec-summary. `--resume` skips if `user_confirmed` and uncontradicted. Done: posture persisted on session-state.
3. **Discover** — For each level in `payload.cascade_levels`, execute [cascade.md](refs/cascade.md) per-level discovery flow. Do not duplicate that ref's steps. Mark `level-<n>` on entry, `compose` after the compose `Task`, `stage-exit` after Gate 6 freeze. Done: level frozen. User pause → checkpoint, skip pre-save, exit.
4. **`--research` / `--challenge`** — Require docs in `--input` or `--output-dir`; else hard-stop `MISSING_DOCS`. Run `python3 scripts/validate_planning.py <output-dir>` from plugin root; pass `payload.static_validation`. `Task` the matching agent per [contracts.md](refs/contracts.md). Persist the report per [output-formats.md](refs/output-formats.md); that persist completes `write`. Done: report written.
5. **write** (discover, after last freeze) — Apply [success-criteria.md](refs/success-criteria.md), then pre-save reflection ([proactivity.md](refs/proactivity.md)), then persist per [output-formats.md](refs/output-formats.md). Pause skips pre-save. Agent JSON parse: one retry, then hard-stop `AGENT_OUTPUT_PARSE_FAILED`. Done: artifacts written.

Load remaining refs on demand from **Shared refs**.

## Interaction boundary

Question surfacing is orchestrator-owned. Discovery runs **inline** in this skill (no discover agent) so question loops stay interactive. Compose/research/challenge `Task` agents are non-interactive; this skill asks and re-invokes. Delivery: [input-resolution.md](refs/input-resolution.md) `question_mode`. Protocol: [goal-anchor.md](refs/goal-anchor.md).

**No per-level challenge agent** — stage-exit is skill-inline; `--challenge` is a full-pass union scan.

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| [cascade.md](refs/cascade.md) | Start of any `--discover` run |
| [project-posture.md](refs/project-posture.md) | Discover start (pre-cascade); resume only if posture unconfirmed or contradicted |
| [note-sessions.md](refs/note-sessions.md) | After every Q&A (classify owner); on level entry (load sidecar) |
| [doc-standards/item-schema.md](refs/doc-standards/item-schema.md) | Discovering/composing any level (IDs, split, spec/build) |
| `refs/doc-standards/<level>.md` | Discovering/composing that level only |
| [goal-anchor.md](refs/goal-anchor.md) | Entire discovery pass (always-on) |
| [proactivity.md](refs/proactivity.md) | Reflect/explore trigger during discovery; PRD cut-pass after MoSCoW; **and** pre-save reflection before write |
| [blind-spots.md](refs/blind-spots.md) | Stage-exit (this level's row) **and** `--challenge` (union) |
| [research-method.md](refs/research-method.md) | Research phase only |
| [output-formats.md](refs/output-formats.md) | Write step; also first Q&A (create/append raw-history) |
| [success-criteria.md](refs/success-criteria.md) | Pre-write gate |
| [contracts.md](refs/contracts.md) | Before any subagent `Task` call |

Phase-specific execution steps stay in `agents/planning/*` — skill does not duplicate agent execution steps.

## Agent delegation

Invoke via `Task` with `PhaseInput` per [contracts.md](refs/contracts.md). Parse per that ref's parsing policy.

| Agent | Path | Contract |
|-------|------|----------|
| compose | `agents/planning/compose.md` | [contracts § compose](refs/contracts.md) |
| research | `agents/planning/research.md` | [contracts § research](refs/contracts.md) |
| challenge | `agents/planning/challenge.md` | [contracts § challenge](refs/contracts.md) |
