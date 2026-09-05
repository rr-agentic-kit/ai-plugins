# rr-planner

Flag-driven **Plan**: full requirements + scored backlog + architecture spine + slice freeze from a frozen `business-case.yaml`. Human index only — runtime is [SKILL.md](SKILL.md) + [refs/](refs/).

## Why

Specify what to build after Discover proved the bet — with system judgment in the same sitting. Refuse Effort-without-architecture, requirement-table shrink-to-ship, smell-fail AC, sprint ceremony, and silent PRD inventiveness when BRD is not frozen.

## What

Owns Plan Q&A, PRD compose/change, standing architecture (+ constitution), feature deltas, WWAS AC, selection status, slice freeze (`execute-slice.yaml`), research, and technical challenge (pre-mortem + red-team). Discover (ES→MRD→BRD + business-case) is `rr-discovery`. Cascade `.md` persists only after `skills/rr-discovery/refs/compose-prose.md` → `rr-humanize`.

**Explicitly no traditional sprints** (no capacity/velocity theater). Sequencing language: **slice / phase / selected requirements**. Release/version bundling of frozen slices is a later Plan add-on — not this skill’s inventiveness.

**Out of scope:** Problem/market/viability/ideation/GTM — route to Discover. Execute / ship-check — future.

## When

### Use when

- Frozen BRD + `business-case.yaml` exist and you need Plan (`--prd`, `--change`, `--freeze-slice`)
- Research or challenge **Plan** docs (`--research`, `--challenge`)
- Shared `--setup` / `--resume` at Plan

### Avoid when

- Problem, market, viability, ideation, beachhead → `rr-discovery`
- Starting Plan without freeze + handoff (entry gate)
- Asking for sprint planning / velocity as Plan process
- Asking this skill to invent a release/version plan this pass

## Actions

| id | outcome | pick when |
|----|---------|-----------|
| `setup` | docs/ framework bootstrap | Shared setup |
| `prd` | Compose PRD + standing Plan path | Entry gate passed |
| `change` | Patch PRD / delta / AC section | `--change` + section + target |
| `freeze-slice` | Mint `execute-slice.yaml` + stamp slice | Selected requirements + smell-clean AC |
| `research` | Cited findings on existing docs | Post-compose |
| `challenge` | Technical pre-mortem + red-team | Prefer Plan targets; compact parent summary |
| `resume` | Continue Plan checkpoint | Paused Plan |

## Technique index

| Technique | Ref |
|-----------|-----|
| Coach / Fast interview | [refs/plan-interview.md](refs/plan-interview.md) |
| RICE / RIC / on-demand lenses | [refs/prioritization-lens.md](refs/prioritization-lens.md) |
| Same-sitting system design | [refs/system-design.md](refs/system-design.md) |
| ADR-lite / supersede | [refs/adr-lite.md](refs/adr-lite.md) |
| Architecture spine | [refs/doc-standards/architecture.md](refs/doc-standards/architecture.md) |
| Constitution | [refs/doc-standards/constitution.md](refs/doc-standards/constitution.md) |
| Feature deltas | [refs/doc-standards/feature-delta.md](refs/doc-standards/feature-delta.md) |
| WWAS + smell gate | [refs/req-smell.md](refs/req-smell.md) |
| Slice freeze kernel | [refs/execute-handoff.md](refs/execute-handoff.md) |
| Technical challenge | [refs/challenge-method.md](refs/challenge-method.md) |

## Philosophy

- **Entry gate** — Frozen BRD + valid `business-case.yaml`
- **Full scope honesty + thin selection** — `_status_:` never deletes the requirement table
- **Spine + deltas + slice kernel** — small standing contracts beat fat PRD dumps to Execute
- **Dual-lens founder** — product + architecture in one sitting
- **Anti-triggers** — Discover flags → `rr-discovery`; sprint language → slice selection

Selectors and depth: [refs/input-resolution.md](refs/input-resolution.md). Shared package → plugin `refs/planning/`.
