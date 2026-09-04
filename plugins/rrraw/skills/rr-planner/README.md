# rr-planner

Flag-driven **Plan**: PRD+ from a frozen `business-case.yaml`. Human index only — runtime is [SKILL.md](SKILL.md) + [refs/](refs/).

## Why

Specify product requirements after Discover has proved the bet. Refuse silent PRD inventiveness when BRD is not frozen or handoff is missing.

## What

Owns Plan Q&A, PRD compose/change, research, and PRD challenge. Discover (ES→MRD→BRD + business-case) is [`rr-discovery`](../rr-discovery/). Cascade `.md` persists only after [compose-prose](../rr-discovery/refs/compose-prose.md) → `rr-humanize`.

**Out of scope:** Problem/market/viability/ideation/GTM framing — route to Discover.

## When

### Use when

- Frozen BRD + `business-case.yaml` exist and you need PRD (`--prd`, `--change`)
- Research or challenge **Plan** docs (`--research`, `--challenge`)
- Shared `--setup` / `--resume` at PRD

### Avoid when

- Problem, market, viability, ideation, beachhead → `rr-discovery`
- Starting Plan without freeze + handoff (entry gate)

## Actions

| id | outcome | pick when |
|----|---------|-----------|
| `setup` | docs/ framework bootstrap | Shared setup |
| `prd` | Compose/freeze PRD | Entry gate passed |
| `change` | Patch PRD section | `--change` + section + target |
| `research` | Cited findings on existing docs | Post-compose |
| `challenge` | Devil's-advocate on PRD | Prefer PRD target |
| `resume` | Continue Plan checkpoint | Paused PRD |

## Philosophy

- **Entry gate** — Frozen BRD + valid `business-case.yaml` (brownfield = one AskQuestion)
- **Item contract** — Same `{DOC}-{n.m}` graph; PRD uses RICE/RIC
- **Humanize** — Same prose gate as Discover
- **Anti-triggers** — Discover flags/NL → `rr-discovery`

Selectors and depth: [refs/input-resolution.md](refs/input-resolution.md). Shared package → plugin `refs/planning/`.
