# rr-discovery

Flag-driven **Discover** for ventures and internal bets. Human index only — runtime policy is [SKILL.md](SKILL.md) + [refs/](refs/).

## Why

Prove a product (venture or internal) exists — problem, market, viability, beachhead — **before** naming Plan capabilities. Freeze to a compact `business-case.yaml` Plan can consume without re-running Discover.

## What

Owns posture, optional ideation, cascade `executive-summary` → `mrd` → `brd`, reverse-from-code compose, challenge (pre-mortem / red-team), and handoff mint. Compose + challenge are `Task` agents; cascade `.md` persists only after humanize (`compose-prose` → `rr-humanize`).

**Out of scope:** PRD / RICE / stories / research reports / launch calendars / architecture authorship as Discover deliverable.

## Actions

| id | outcome | pick when |
|----|---------|-----------|
| `setup` | docs/ framework + SoT load line | Bootstrap / repair only |
| `discover` | Cascade through BRD + freeze handoff | New or continue Discover (interview) |
| `from-code` | Reverse compose ES→MRD→BRD at `code-extraction` | Existing product source; no freeze until shaped to `draft` |
| `change` | Patch frozen Discover stem | `--change` + section + target on ES/MRD/BRD |
| `challenge` | Pre-mortem / red-team report (**standard**; add `deep` for exhaustive) | Existing Discover docs |

`--resume` is a **selector** (continue checkpoint), not a primary action — [input-resolution.md](refs/input-resolution.md).

## When

### Use when

- Proving a bet before PRD (`--discover` / `--executive-summary` / `--mrd` / `--brd`)
- Reverse Discover docs from shipped code (`--from-code`)
- Bootstrap or repair `docs/` (`--setup`) — does not start discover
- Continue a paused Discover session (`--resume` selector) or challenge ES/MRD/BRD (`--challenge`)

### Avoid when

- Need Plan (PRD / research / feature backlog) → `rr-planner`
- Implementation, code review, tickets, analytics/CI (unless intent is Discover docs from source)

## Philosophy

- **Hard freeze** — Plan refuses entry without frozen BRD + valid `business-case.yaml`; `code-extraction` blocks freeze
- **Layered scrutiny** — Auto-reflection → smells → `--challenge` (standard) → `--challenge deep` (`refs/planning/challenge-layers.md`); smell-clean ≠ challenged
- **No fabricated TAM** — `hold` / `vague` beat fake precision (including from-code reverse)
- **Humanize** — Cascade prose is not AI-slop; machine files skip humanize
- **Anti-triggers** — Features/RICE/launch calendars park to Plan or notes
- **Backward-chain** — When MRD/BRD cannot support the goal given parents, challenge upstream (MRD↔ES, BRD↔MRD) — do not bury as HOLD

## UX

Process-ownership (user is not process-owner): [`../../INTENT.md`](../../INTENT.md) UX. Skill-local chrome below.

### Invoke

Flags (`--setup` / `--discover` / `--from-code` / `--challenge` / `--challenge deep` / …) or clear Discover NL; bare invoke never silent-rediscovers.

### Intake

Status-first (summary → phase status + session-state); resolve emits payload before cascade. From-code: research root = `--input` or `PROJECT_ROOT`.

### Clarify

**Interview discover:** AskQuestion on vague posture/domain, binding panel `hold`, missing freeze fields, or **risk-accept** — do not invent.

**From-code:** contradictions / mutually exclusive readings / blocking coherence only — not a polish interview. Cap stays `questions_per_cycle`.

### Output

Cascade stems + handoff on BRD freeze; from-code stems stay `maturity: code-extraction` until shape/resume; challenge reports when standard/deep requested; machine files skip humanize.

### Close

Session-state + status stamps written. **Next Up** per `refs/planning/progress.md`: after freeze → Plan (`rr-planner`) only when standard challenge clear or risk-accept for load-bearing stems; after from-code → shape/resume (promote to `draft`) or `--challenge`. Do not incentivize skip.

## Technique refs

| Ref | Role |
|-----|------|
| [from-code](refs/from-code.md) | Reverse Discover from codebase |
| [ideation](refs/ideation.md) | Brainstorm, OST, assumptions, pretotype |
| [interview-method](refs/interview-method.md) | Mom Test + JTBD (on demand) |
| [strategy-lenses](refs/strategy-lenses.md) | Startup Canvas default; Lean/BMC/SWOT/VP on demand |
| [gtm-framing](refs/gtm-framing.md) | Beachhead, ICP, motion — stop before launch |
| [challenge-method](refs/challenge-method.md) | Pre-mortem + strategy red-team |
| [business-case-handoff](refs/business-case-handoff.md) | Compact Plan handoff |
| [compose-prose](refs/compose-prose.md) | Humanize gate before cascade `.md` persist |

## Constraints

- **Invoke:** Auto — no `disable-model-invocation`; ambient WHEN description is enough
- **Gates:** BRD freeze + humanize before cascade `.md` persist; no fabricated TAM; no freeze while `code-extraction`
- **Paths:** Plugin-root relative only — no `..` in skill/ref markdown
- **Eval-first:** Fix FAIL audit ids only; preserve outcome (no redesign)

## Notes

- **Version law (Shared):** `refs/planning/baselines.md` — flow skills only; no skill-local version stubs. Non-loaders: humanize, git helpers, rr-test. Index: `refs/planning/README.md`
- Shared ledger / items / setup: plugin `refs/planning/` (link there directly — no skill stubs)
- Bare invoke never silent-rediscovers — [refs/input-resolution.md](refs/input-resolution.md)
- Technique refs above are skill-local under `skills/rr-discovery/refs/`
- `docs/agent.plan.md` is tripwire only — refuse non-patch; route here or `rr-planner`
