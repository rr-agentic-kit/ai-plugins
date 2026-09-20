# CE report lean JSON (improve emit)

**Retired field tables.** Per-kind output contracts are JSON Schema — agents **Read** the matching `*.schema.json` only (never `*.md.j2`):

| Kind | Schema | Render |
|------|--------|--------|
| `compliance` | [`reports/compliance.schema.json`](reports/compliance.schema.json) | `python3 scripts/render_ce_report.py compliance …` |
| `opportunity` | [`reports/opportunity.schema.json`](reports/opportunity.schema.json) | `… opportunity …` |
| `apply-plan` | [`reports/apply-plan.schema.json`](reports/apply-plan.schema.json) | `… apply-plan …` |
| `reflection` | [`reports/reflection.schema.json`](reports/reflection.schema.json) | `… reflection …` |

Pattern SoT (when to lean-emit, validate→fix loop, target-skill layout): [`reports/README.md`](reports/README.md).

Standalone **audit** / **audit-redesign** may still emit full markdown in chat; improve **must** use lean JSON + render.
