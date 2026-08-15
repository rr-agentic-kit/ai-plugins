---
name: rr-planner
description: Flag-driven software planning docs — progressive top-down discovery (exec-summary → MRD → BRD → PRD → FRD), compose, research, and challenge. Orchestrates phase agents under agents/planning/*; no command files.
---

# rr-planner (runtime)

**Human overview:** [README.md](README.md)

## Interaction boundary

Question surfacing is orchestrator-owned. `Task` subagents are non-interactive and return one message.

| Concern | Owner |
|---------|-------|
| Discovery (disambiguate, clarify, confirm nuance) | **Skill (inline)** — surfaces questions per `question_mode` |
| Compose, research, challenge | **Task subagents** — return `clarifications_needed[]` on gaps; skill surfaces and re-invokes |
| User prompts | **Never** from subagents |

### Question modes

| Mode | Flag | Behavior |
|------|------|----------|
| **Ask** (default) | _(none)_ | Use `AskQuestion` for structured options |
| **Text** | `--text-mode` | Ask inline in chat; user replies in conversation |

Both modes follow the same [goal-anchor](refs/goal-anchor.md) protocol. Only the delivery mechanism differs.

### Clarification loop

Loops continue until **all** of:

- No pending `clarifications_needed[]` from agents
- No blocking discovery gaps at the current level
- User confirms done for the level or session ("done", "that's enough", "good to proceed", etc.)

There is **no round cap**. User may stop at any time → checkpoint and resume later.

## Activation

1. Read [refs/input-resolution.md](refs/input-resolution.md) — normalize raw flags and prompt into canonical payload **before** any agent call.
2. Load shared refs on demand per phase (see **Shared refs** below).
3. Route to inline discovery, one agent, or deterministic phase chain.
4. Write artifacts to `--output-dir` via [refs/output-formats.md](refs/output-formats.md).

Agents under `agents/planning/*` are function-style executors: they receive normalized payload, return typed output, and do not own routing, continuation, or user interaction.

## Cascade model

Progressive top-down discovery; each level inherits and narrows the level above:

```
exec-summary (vision / problem / why)
  → mrd (market)
    → brd (business requirements)
      → prd (product requirements)
        → frd (functional detail)
```

Level order, inheritance rules, and per-level gates: [refs/cascade.md](refs/cascade.md).
Doc structure per level: [refs/doc-standards/](refs/doc-standards/). Shared item contract: [refs/doc-standards/item-schema.md](refs/doc-standards/item-schema.md).

## Primary action flags

Exactly one required per invocation (see [input-resolution](refs/input-resolution.md)):

| Flag | Handler |
|------|---------|
| `--discover` (default) | Inline discovery → cascade all levels → compose each |
| `--all` | Same as `--discover` |
| `--exec-summary` | Inline discovery + compose for exec-summary only |
| `--mrd` | Inline discovery + compose for MRD (inherits exec-summary facts) |
| `--brd` | Inline discovery + compose for BRD |
| `--prd` | Inline discovery + compose for PRD |
| `--frd` | Inline discovery + compose for FRD |
| `--research` | research agent (post-composition market evaluation) |
| `--challenge` / `--review` | challenge agent (critique existing docs) |

Shared selectors: `--input`, `--output-dir`, `--format`, `--depth`, `--text-mode`, `--resume` — normalized by [input-resolution](refs/input-resolution.md); defaults in [README](README.md).

## Runtime flow

```
raw input → input-resolution (normalize) → [resume? load checkpoint]
  → [discover inline + question loops; append raw-history YAML each Q&A]
  → compose agent(s) per level
  → stage-exit blind-spots (this level's row) → freeze
  → [optional research / challenge]
  → success-criteria gate → pre-save reflection → write md|yaml docs
  → write items.json + session-state.json → checkpoint
```

Pause checkpoints without pre-save reflection. Composed docs wait for stage-exit + pre-save.

### Default `--discover` chain

1. Load [refs/cascade.md](refs/cascade.md). If `--resume`, load `session-state.json` from `--output-dir` and continue from checkpoint. Append further Q&A to `raw_history_path` (create `raw-history/{UTC}.yaml` if missing).
2. For each cascade level (exec-summary → mrd → brd → prd → frd):
   - Load matching `refs/doc-standards/<level>.md` and [refs/doc-standards/item-schema.md](refs/doc-standards/item-schema.md) for the current level.
   - Load [refs/goal-anchor.md](refs/goal-anchor.md) for the **entire** discovery pass at this level (not on a trigger). Unclear or ambiguous statements are blocking — do not record as fact until resolved or explicitly accepted as `assumption` with `blocking` set.
   - Run inline discovery for that level (inherit facts from prior levels). After every Q&A round, append a turn to `raw-history/{UTC}.yaml`.
   - On reflect/explore trigger → load [refs/proactivity.md](refs/proactivity.md) (discovery-time Gate 5; `standard`/`deep` only).
   - Invoke `compose` agent with `doc_type` = level.
   - While `clarifications_needed[]` non-empty → surface question → append raw-history → merge answers → re-invoke compose.
   - Load [refs/blind-spots.md](refs/blind-spots.md). Skill-inline scan **this level's applicability row** (`in_scope` + `inherit_check` only). `critical`/`high` → questioning before freeze; `medium`/`low` → assumptions/open questions. User may explicitly accept remaining. Findings that belong in the doc merge via re-compose. Do **not** spawn the challenge agent per level.
   - Gate: level completion criteria in cascade.md must pass before next level (static: `python3 scripts/validate_planning.py <output-dir>` from plugin root). Freeze the level on pass.
   - User may stop anytime → checkpoint `session-state.json` + `items.json` + raw-history; skip pre-save; exit cleanly. Do not write composed docs on pause unless already frozen.
3. Optional: invoke `research` agent when `--research` flag or user requests market validation.
4. Apply [refs/success-criteria.md](refs/success-criteria.md) gate before final write.
5. Pre-save reflection ([proactivity.md](refs/proactivity.md) § Pre-save): all depths; one pass + max one fix cycle. Pause does not trigger this.
6. Write human docs (`md` or `yaml`) then `items.json` + `session-state.json`. Checkpoint session state to `--output-dir`.

### `--challenge` / `--review` chain

1. Load existing docs from `--input` or `--output-dir`.
2. Run `python3 scripts/validate_planning.py <output-dir>` from plugin root. Pass the result into the agent as `payload.static_validation` (`passed` / `failed` / `skipped`). Do not ask the challenge agent to re-check refs.
3. Load [refs/blind-spots.md](refs/blind-spots.md). Challenge scans the **union** of all applicability rows (full taxonomy), not a per-level `in_scope` slice.
4. Invoke `challenge` agent. Write `challenge-report.md` or `challenge-report.yaml` per `--format`.
5. Surface findings; user may re-run `--discover` with refinements.

### Orchestration gates

| Gate | Rule |
|------|------|
| **Level inheritance** | Child level must not contradict parent facts; conflicts → goal-anchor + question |
| **Clarify (always-on)** | Unclear/ambiguous statements block the level; do not record as fact until resolved or accepted as `assumption` |
| **Level completion** | Per-level done-when in cascade.md + doc-standards before advancing |
| **Stage-exit blind-spots** | Scan this level's row; `critical`/`high` resolved or accepted before freeze |
| **Clarification loop** | Re-invoke compose after each answer until no pending clarifications or user says done |
| **Stop / resume** | User stop → checkpoint (no pre-save); `--resume` reloads `session-state.json` and appends the same raw-history file |
| **Success criteria** | Static: `validate_planning.py` parent walk + spec/build. Judgment: atomic leaves, rank inflation, triad/AC quality |
| **Pre-save reflection** | After success-criteria, all depths, one pass + one fix cycle; then write |
| **Parse retry** | One retry on agent JSON parse failure; second failure → hard-stop |

## Output

| Artifact | Location |
|----------|----------|
| Per-doc files | `--output-dir` (default `{PROJECT_ROOT}/docs/plans/`) — `exec-summary`, `mrd`, `brd`, `prd`, `frd` with `.md` or `.yaml` |
| Item graph | `--output-dir/items.json` (always; validator target) |
| Session checkpoint | `--output-dir/session-state.json` (always; resume + agent I/O) |
| Q&A history | `--output-dir/raw-history/{UTC compact ISO-8601}.yaml` (append after each Q&A) |
| Format | `--format` `md` (default) or `yaml` — [refs/output-formats.md](refs/output-formats.md). JSON is not a plan-doc format |

`PROJECT_ROOT` = git toplevel else workspace root. `--output-dir` wins. Old `docs/planning/` checkpoint: auto-resume once, state the new default, do not copy files — [input-resolution](refs/input-resolution.md).

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| [cascade.md](refs/cascade.md) | Start of any `--discover` run |
| [doc-standards/item-schema.md](refs/doc-standards/item-schema.md) | Discovering/composing any level (IDs, split, spec/build) |
| `refs/doc-standards/<level>.md` | Discovering/composing that level only |
| [goal-anchor.md](refs/goal-anchor.md) | Entire discovery pass (always-on; unclear + ambiguous are blocking) |
| [proactivity.md](refs/proactivity.md) | Reflect/explore trigger during discovery; **and** pre-save reflection before write |
| [blind-spots.md](refs/blind-spots.md) | Stage-exit (this level's row) **and** `--challenge` (union) |
| [research-method.md](refs/research-method.md) | Research phase only |
| [output-formats.md](refs/output-formats.md) | Write step; also first Q&A (create/append raw-history) |
| [success-criteria.md](refs/success-criteria.md) | Pre-write gate |
| [contracts.md](refs/contracts.md) | Before any subagent `Task` call |

Phase-specific execution steps stay in `agents/planning/*` — skill does not duplicate agent execution steps.

## Agent delegation

Invoke via `Task` with `PhaseInput` per [refs/contracts.md](refs/contracts.md). Parse agent JSON: one retry on failure, then hard-stop.

| Agent | Path | Contract |
|-------|------|----------|
| compose | `agents/planning/compose.md` | [contracts § compose](refs/contracts.md) |
| research | `agents/planning/research.md` | [contracts § research](refs/contracts.md) |
| challenge | `agents/planning/challenge.md` | [contracts § challenge](refs/contracts.md) |

**No discover agent** — discovery runs inline in this skill to preserve interactive question loops.
**No per-level challenge agent** — stage-exit blind-spots are skill-inline; `--challenge` is a full-pass union scan only.
