# rr-main

Interactive **plugin guide**: orient, explain, situate, suggest next — and only after confirm, hand off to a peer skill. Human index only — runtime is [SKILL.md](SKILL.md) + [refs/](refs/).

## Why

Founders, engineers, and operators land in RRRaw without a map: which skill owns Discover vs Plan vs Build vs CI, what is frozen, and what to run next. **rr-main** answers from catalog + live status and never steals the turn into Discover/Plan/Build/CI side effects. Done when the user knows where they are and either stops informed or accepts a confirmed peer handoff.

## What

Owns action classify (orient / explain / situate / suggest / handoff), role cheat sheets, public skill catalog answers, read-only status situate, Next Up suggestions, and confirm-before-handoff to a peer `SKILL.md`.

**Out of scope:** Minting versions, freeze, writing `docs/rr/`, cascade/slice/CI execution, replacing plugin `INTENT.md` or the plugin README as static Spec/overview.

## Actions

| id | Outcome | Pick when |
|----|---------|-----------|
| `orient` | Brief plugin pitch + role cheat sheets | Bare invoke / `--help` / “what is this” |
| `explain` | How a skill / flag / phase / concept works | “how does X work”, skill name in ask |
| `situate` | Where you are + current project state (read-only) | “where am I”, “status”, “what’s frozen” |
| `suggest` | Next Up options (no execution) | “what next”, stuck, after situate |
| `handoff` | After confirm → peer `SKILL.md` + purpose | Unambiguous “do X now” **or** user accepts handoff offer |

## When

### Use when

- First landing or “what is RRRaw / which skill do I use”
- Explaining a public skill, flag, phase, or plugin concept without running it
- Checking status / freeze / phase (read-only) or asking what to do next
- Ready to run a peer skill and willing to confirm the handoff

### Avoid when

- Ambient “just build it” / silent Discover/Plan/CI — stay suggest + handoff offer; do not silent-run
- Replacing peer Procedure (cascade, slice pipeline, forge ship) — route, do not reimplement
- Treating this skill as Auto-invoke ambient owner — Self-invoke only
- Expecting writes to `docs/rr/`, version mint, freeze, or host CI from this skill

## Philosophy

- **Answer + suggest** — default posture; no Discover/Plan/Build/CI side effects in-main
- **Confirm-before-handoff** — never silent peer Procedure; AskQuestion (text fallback) then peer SKILL invoke
- **Route, don’t reimplement** — overlap with peer skills → handoff offer or explain pointer
- **Status-first, read-only** — situate mirrors spine glance; missing docs → say so + setup Next Up
- **Role-filtered, not exhaustive** — cheat sheets are “most useful,” not every flag

## UX

Process-ownership (user is not process-owner): plugin `INTENT.md` UX. Skill-local chrome below.

### Invoke

Bare `@rr-main` / `/rr-main`, `--help`, or clear NL (orient / explain / status / what next / do X). Flags optional; no slash-command process layer.

### Intake

Resolve classifies bare → `orient`; NL/flags → one action + payload. Prefer AskQuestion only for ambiguous action (≤2 options) or role when orient needs a filter.

### Clarify

AskQuestion for role filter, action ambiguity, and handoff confirm. Text-mode: same options as prose; do not stall.

### Output

Pitch / explanation / status glance / Next Up list. Optional handoff offer. No peer Procedure body, no `docs/rr/` writes, no code/CI from this skill.

### Close

Answer actions stop after answer + optional suggestions. On handoff accept → peer SKILL invoke (Task or Read peer `SKILL.md` + purpose); **rr-main stops owning the turn**. On decline → stay in suggest.

## Constraints

- **Invoke:** Manual `@rr-main` / slash — `disable-model-invocation: true`; outcome-first description
- **Gates:** Confirm before any peer SKILL invoke; situate never mutates; no silent builder/planner/CI
- **Paths:** Plugin-root relative only — no `..` in skill/ref markdown
- **Catalog:** List only skills in `plugin.json` `skills[]` — do not invent unlisted skills (e.g. absent `rr-test`)
- **Eval-first:** Fix FAIL audit ids only; preserve outcome (no redesign)

## Notes

- Peer skill Procedures live under `skills/<peer>/` — this skill only confirms then invokes
- Role SoT: [refs/role-map.md](refs/role-map.md); catalog SoT: [refs/skill-catalog.md](refs/skill-catalog.md)
- Static Spec/overview remain plugin `INTENT.md` and plugin `README.md`
