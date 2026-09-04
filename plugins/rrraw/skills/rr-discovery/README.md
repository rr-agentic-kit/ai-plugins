# rr-discovery

Flag-driven **Discover** for ventures and internal bets. Human index only — runtime policy is [SKILL.md](SKILL.md) + [refs/](refs/).

## Why

Prove a product (venture or internal) exists — problem, market, viability, beachhead — **before** naming Plan capabilities. Freeze to a compact `business-case.yaml` Plan can consume without re-running Discover.

## What

Owns posture, optional ideation, cascade `executive-summary` → `mrd` → `brd`, challenge (pre-mortem / red-team), and handoff mint. Compose + challenge are `Task` agents; cascade `.md` persists only after humanize (`compose-prose` → `rr-humanize`).

**Out of scope:** PRD / RICE / stories / research reports / launch calendars / architecture authorship as Discover deliverable.

Shared ledger / items / baselines: `plugins/rrraw/refs/planning/`.

## When

### Use when

- Proving a bet before PRD (`--discover` / `--executive-summary` / `--mrd` / `--brd`)
- Bootstrap or repair `docs/` (`--setup`) without starting compose
- Resume discovery (`--resume`) or challenge ES/MRD/BRD (`--challenge`)

### Avoid when

- PRD compose, feature backlog, or post-compose research → `rr-planner`
- Implementation, code review, tickets, analytics/CI

## Actions

| id | outcome | pick when |
|----|---------|-----------|
| `setup` | docs/ framework + SoT load line | Bootstrap / repair only |
| `discover` | Cascade through BRD + freeze handoff | New or continue Discover |
| `change` | Patch frozen Discover stem | `--change` + section + target on ES/MRD/BRD |
| `challenge` | Pre-mortem / red-team report | Existing Discover docs |
| `resume` | Continue checkpoint | Paused Discover session |

## Philosophy

- **Hard freeze** — Plan refuses entry without frozen BRD + valid `business-case.yaml`
- **No fabricated TAM** — `hold` / `vague` beat fake precision
- **Humanize** — Cascade prose is not AI-slop; machine files skip humanize
- **Anti-triggers** — Features/RICE/launch calendars park to Plan or notes

## Technique refs

| Ref | Role |
|-----|------|
| [ideation](refs/ideation.md) | Brainstorm, OST, assumptions, pretotype |
| [interview-method](refs/interview-method.md) | Mom Test + JTBD (on demand) |
| [strategy-lenses](refs/strategy-lenses.md) | Startup Canvas default; Lean/BMC/SWOT/VP on demand |
| [gtm-framing](refs/gtm-framing.md) | Beachhead, ICP, motion — stop before launch |
| [challenge-method](refs/challenge-method.md) | Pre-mortem + strategy red-team |
| [business-case-handoff](refs/business-case-handoff.md) | Compact Plan handoff |
| [compose-prose](refs/compose-prose.md) | Humanize gate before cascade `.md` persist |

Bare invoke never silent-rediscovers — [refs/input-resolution.md](refs/input-resolution.md).
