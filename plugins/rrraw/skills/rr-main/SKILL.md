---
name: rr-main
description: rr-main — orient, explain, situate, or suggest next; confirm before handing off to a peer skill.
disable-model-invocation: true
---

# rr-main

**Human overview:** [README.md](README.md)

## Purpose

Interactive plugin guide for Founder-PM / Engineer / Operator. Answers from role map + skill catalog + read-only status; suggests Next Up; only after confirmed execute-intent does it invoke a peer `SKILL.md` (+ purpose) and stop owning the turn. Never Discover/Plan/Build/CI side effects in-main.

## When to use

- First landing or “what is RRRaw / which skill do I use”
- Explaining a public skill, flag, phase, or plugin concept without running it
- Checking status / freeze / phase (read-only) or asking what to do next
- Ready to run a peer skill and willing to confirm the handoff

## When not to use

- Ambient “just build it” / silent Discover/Plan/CI — stay suggest + handoff offer; do not silent-run
- Replacing peer Procedure (cascade, slice pipeline, forge ship) — route, do not reimplement
- Treating this skill as Auto-invoke ambient owner — Self-invoke only
- Expecting writes to `docs/rr/`, version mint, freeze, or host CI from this skill

## Actions

| id | Outcome |
|----|---------|
| `orient` | Brief plugin pitch + role cheat sheets |
| `explain` | How a skill / flag / phase / concept works |
| `situate` | Where you are + current project state (read-only) |
| `suggest` | Next Up options (no execution) |
| `handoff` | After confirm → peer `SKILL.md` + purpose |

## Procedure

TodoWrite `merge: false` with ids `resolve`, `load`, `answer` when the run spans answer-only; add `handoff` when execute-intent is detected or user asked to run. Mark `completed` before advancing. Single unambiguous orient with no clarify: omit TodoWrite (single-shot N/A).

**Delivery channels:** Prefer AskQuestion for role filter, action ambiguity (≤2 options), and handoff confirm; text-mode same options; do not stall.

1. **resolve** — Load [refs/input-resolution.md](refs/input-resolution.md). Classify bare / `--help` / “what is this” → `orient`; NL/flags → exactly one action; emit payload. AskQuestion only for ambiguous action (≤2) or role when orient needs a filter. Done: payload emitted. Stop: that ref’s deterministic errors.
2. **load** — Progressive disclosure (one hop from this file only):
   - Always for `orient` / `explain`: [refs/role-map.md](refs/role-map.md) + [refs/skill-catalog.md](refs/skill-catalog.md)
   - For `situate` / `suggest`: also [refs/situate.md](refs/situate.md)
   - For `handoff` or when execute-intent detected: also [refs/handoff.md](refs/handoff.md)
   Done: required refs for `payload.action` loaded. Do **not** Read peer `refs/` to do their job.
3. **answer** — When `payload.action` is `orient` | `explain` | `situate` | `suggest`: produce answer + optional Next Up / handoff **offer**. **Stop.** No peer Procedure, no writes to `docs/rr/`, no code/CI. Optional offer does not invoke peer until step 4.
4. **handoff** (optional) — Only when execute-intent is unambiguous **or** user accepted a handoff offer. Load [refs/handoff.md](refs/handoff.md) if not already. Confirm target skill + purpose (AskQuestion / text). On accept: peer SKILL invoke (Task or Read peer `SKILL.md` + purpose — same pattern as planner↔builder); **rr-main stops owning the turn**. On decline → stay in suggest (re-enter answer posture). Anti-trigger: ambient “just build it” without confirm → suggest + offer only.

## Progressive disclosure

| Ref | When |
|-----|------|
| [refs/input-resolution.md](refs/input-resolution.md) | Every invocation |
| [refs/role-map.md](refs/role-map.md) | `orient` / `explain` |
| [refs/skill-catalog.md](refs/skill-catalog.md) | `orient` / `explain` |
| [refs/situate.md](refs/situate.md) | `situate` / `suggest` |
| [refs/handoff.md](refs/handoff.md) | Execute-intent or user asked to run |

## Orchestration

AskQuestion gates: role filter, action ambiguity (≤2), handoff confirm. Prefer AskQuestion; text-mode same options mandatory; do not stall. After peer invoke, do not continue rr-main Procedure in the same turn.
