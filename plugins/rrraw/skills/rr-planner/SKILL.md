---
name: rr-planner
description: Flag-driven software planning docs — progressive top-down discovery (exec-summary → MRD → BRD → PRD), compose, research, and challenge. Use when producing exec-summary → PRD planning docs, bootstrapping docs/plans (--setup), resuming a checkpoint, or researching/challenging existing ones. Orchestrates phase agents under agents/planning/*; no command files.
---

# rr-planner

**Human overview:** [README.md](README.md)

## Purpose

Produce cascade planning docs (exec-summary → PRD) from flags and conversation. This skill owns question loops and routing. Compose, research, and challenge run as non-interactive `Task` agents under `agents/planning/*`.

## When to use

- Bootstrap or repair the plans directory (`--setup`) — does not start discover
- Discover a product or plan (`--discover` / `--all`, or a cascade level flag)
- Change a frozen or shipping track (`--change` with `--section` + `--target`)
- Resume a paused session (`--resume`)
- Research or challenge **existing** planning docs

## When not to use

- Implementation, code review, or ticket writing that is not cascade planning
- Artifact-type advice (skill vs command, process checklist) that is not a product to plan
- Inventing docs to run research or challenge — those actions require existing docs ([input-resolution.md](refs/input-resolution.md))
- Inventing a skip of parent cascade levels — level flags expand ancestors; `depth: shallow` is the only trim ([input-resolution.md](refs/input-resolution.md))

Code/ticket work and artifact-type advice stop at resolve via `OUT_OF_SCOPE` unless a primary flag is present ([input-resolution.md](refs/input-resolution.md)).

## Procedure

TodoWrite `merge: false` before step 1 with stable ids `resolve`, `posture`, `premise`, `level-<n>` (one per `payload.cascade_levels` entry), `sweep`, `compose`, `stage-exit`, `verdict`, `write`. Mark `completed` before advancing. Re-add `sweep`, `compose`, `stage-exit`, and `verdict` with `merge: true` when entering the next level. Omit `posture` / `premise` / `level-*` / `sweep` / `compose` / `stage-exit` / `verdict` when `action` is `research` or `challenge`. When `action` is `setup`: only `resolve`, `setup`.

Phrases: [progress.md](refs/progress.md) on every invocation (`verifying <section>` then `<section> is created` / `is fixed` / `was ok` / `is failed`).

1. **resolve** — Load [input-resolution.md](refs/input-resolution.md) (status-first pick from `docs/plans/status.yaml`). Normalize raw flags and NL into `NormalizedPayload`. If `output_dir` (or a cascade `--input` dir) already has cascade docs, print `verifying cascade format` and run `sh scripts/validate_planning.sh --rewrite <dir>` before any `Task` ([setup.md](refs/setup.md) section names). If `status.yaml` or `agent.plan.md` exists in the plans root — or this is first compose — print `verifying agent.plan.md` / `verifying root SoT load line` and sync injection: `sh scripts/validate_planning.sh --sync-agent-config --repo-root <PROJECT_ROOT> <plans-root>` ([agent-config.md](refs/agent-config.md)). Done: payload emitted; stale md/yaml rewritten; load line present on existing root SoT. Stop: that ref's deterministic errors; pairing stops in [baselines.md](refs/baselines.md) (skill classify — not validator FAILs).

Branch on `payload.action`. Do not run the sibling primary path. Bare invoke never silent-rediscovers when plans already exist (`payload.route: ask`). `--setup` never starts discover.

| `payload.action` | Next | Todos after `resolve` |
|------------------|------|------------------------|
| `setup` | step 2 (completes `write`). Stop. Do not posture. | `setup` |
| `discover`, `exec-summary`…`prd`, `change` | step 3, then step 5 | `posture`, `premise`, `level-*`, `sweep`, `compose`, `stage-exit`, `verdict`, `write` |
| `research`, `challenge` | step 4 (completes `write`) | `write` only |

If `payload.chain` includes `research` and/or `challenge`, run step 4 after step 3 (last level frozen; docs on disk) and before step 5. Do not start a second discover pass.

2. **setup** — Load [setup.md](refs/setup.md). Run `sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT> <plans-dir>`. For each TSV line, print the [progress.md](refs/progress.md) pair. Completes `write`. Done: that ref's done-when. Stop: any section `failed` (script exit non-zero). Do not start discover.

3. **discover** — Load [project-posture.md](refs/project-posture.md) (includes `domain_context`). Done: that ref's persist condition. Then for each level in `payload.cascade_levels`, execute [cascade.md](refs/cascade.md). Mark `level-<n>` on entry, `sweep` after the re-decision sweep, `premise` after the exec-summary premise test (skip the id on later levels), `compose` after the compose `Task`, `stage-exit` after Gate 6, `verdict` after Gate 7. After compose persist: if that doc's `challenge.status` is `clean` or `dirty-accepted`, set `dirty` ([baselines.md](refs/baselines.md)). Freeze does not wait on challenge-clean. Done: last listed level frozen. Stop/pause: cascade.md.

4. **research / challenge** — Load [contracts.md](refs/contracts.md). Research also loads [research-method.md](refs/research-method.md); challenge also loads [blind-spots.md](refs/blind-spots.md) and [decision-ledger.md](refs/decision-ledger.md). `Task` the matching agent. Research: agent returns when its iteration budget is exhausted (`ok`, or `partial` + `clarifications_needed`); skill may re-`Task` or stop when the user confirms done. Persist the report per [output-formats.md](refs/output-formats.md). Research persist completes `write`. Challenge: overwrite `challenge-report.md` (latest scan is the worklist). Stamp `status.yaml` `challenge:` from findings — `clean` iff no findings for that `doc` stem and `scanned_digest` recorded from the live digest. If any `dirty`: AskQuestion — **Address now** | **Accept residual (`dirty-accepted`)** | **Done for now** (leave `dirty`). Address now → re-enter discover/compose for affected stems (from `doc`) → AskQuestion **Challenge again?** No cycle cap. Stop: all `clean`, user `dirty-accepted`, user done-for-now, or pause. Freeze (Gates 1–7) does not wait on this. `depth: deep` still chains it after last freeze. `final_status: ok` allowed with `dirty-accepted`; leftover `dirty` (not accepted) stays `partial` at chain exit unless the user picks accept or done-for-now. Challenge persist plus the address-loop exit completes `write`. Done: report written; attestation stamped. Stop: input-resolution deterministic errors; contracts parsing policy.

5. **write** (discover/change only, after last freeze and any `payload.chain` phases) — Apply [success-criteria.md](refs/success-criteria.md), then pre-save reflection ([proactivity.md](refs/proactivity.md)), then persist `session-state.json` and `status.yaml` per [output-formats.md](refs/output-formats.md) / [baselines.md](refs/baselines.md). Print [progress.md](refs/progress.md) for `status.yaml` / `agent.plan.md` writes and freeze mint. On **first compose** into a repo: write `status.yaml`, write `agent.plan.md`, sync the one-liner into existing root agent SoT files, set `claude_config_version`. Leftover challenge `dirty` (not accepted) keeps `final_status: partial`. `dirty-accepted` does not block `ok`. Done: session-state + status written. Stop: contracts parsing policy.

Load remaining refs on demand from **Shared refs**.

## Shared refs (load on demand)

| Ref | When |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Every invocation |
| [progress.md](refs/progress.md) | Every invocation |
| [setup.md](refs/setup.md) | `action: setup`; resolve rewrite/sync (section names) |
| [baselines.md](refs/baselines.md) | Every resolve; freeze / `--change` / open-next; first compose; challenge stamp |
| [agent-config.md](refs/agent-config.md) | Resolve sync; first compose; `--setup`; `claude_config_version` lag |
| [cascade.md](refs/cascade.md) | Discover-path actions (`discover`, `--change`, or a cascade level flag) |
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
| [output-formats.md](refs/output-formats.md) | After compose; skill write of session-state / status.yaml / agent.plan.md / future.md / tech.md / later.md / raw-history / notes; first Q&A |
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
