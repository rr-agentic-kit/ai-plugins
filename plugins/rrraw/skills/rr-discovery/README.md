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
| `challenge` | Pre-mortem / red-team report | Existing Discover docs |

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
- **No fabricated TAM** — `hold` / `vague` beat fake precision (including from-code reverse)
- **Humanize** — Cascade prose is not AI-slop; machine files skip humanize
- **Anti-triggers** — Features/RICE/launch calendars park to Plan or notes

## UX

### Invoke

Flags (`--setup` / `--discover` / `--from-code` / `--challenge` / …) or clear Discover NL; bare invoke never silent-rediscovers.

### Intake

Status-first (summary → phase status + session-state); resolve emits payload before cascade. From-code: research root = `--input` or `PROJECT_ROOT`.

### Clarify

**Interview discover:** AskQuestion on vague posture/domain, binding panel `hold`, or missing freeze fields — do not invent.

**From-code:** contradictions / mutually exclusive readings / blocking coherence only — not a polish interview. Cap stays `questions_per_cycle`.

### Output

Cascade stems + handoff on BRD freeze; from-code stems stay `maturity: code-extraction` until shape/resume; challenge reports when requested; machine files skip humanize.

### Close

Session-state + status stamps written. **Next Up:** after freeze → Plan (`rr-planner`); after from-code → shape/resume (promote to `draft`) or `--challenge`.

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

- Shared ledger / items / baselines: plugin `refs/planning/` (link there directly — no skill stubs)
- Bare invoke never silent-rediscovers — [refs/input-resolution.md](refs/input-resolution.md)
- Technique refs above are skill-local under `skills/rr-discovery/refs/`
