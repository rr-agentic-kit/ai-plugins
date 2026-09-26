# architecture (tech ADRs)

**Audience: dual** — `refs/planning/doc-standards/dual-audience.md`  
**Owner:** True **technical** Architecture Decision Records — stack, integration boundaries, data-model standing choices. Plan authors ADRs when Effort drivers need them; **s-prepare** may mint/revise build-blocking `ADR-n` **only when forced** by L1/L2 (lazy — not a pre-pass dump). Product DEC/constitution stay Plan-owned.

**Path:** `docs/rr/{track}/plan/architecture.md` and/or `adrs/`  
**Load when:** On-demand when a capability cites a tech ADR; not the always-load standing law ([constitution.md](constitution.md)).

**Does not:** Hold product UX baselines, Bind/Prevent/Rule product constitution, or feature mechanism. Those live in `constitution.md` / `deltas/`. Does not invite C4 sprawl or ADR catalogs as context dumps.

## When to use

| Use architecture / ADR | Use elsewhere |
|------------------------|---------------|
| Stack / runtime choice that binds implementers | Product non-negotiables → constitution INDEX |
| Integration boundary / protocol standing choice | Feature mechanism + Effort drivers → `deltas/<id>.md` |
| Data-model standing choice across features | Global UX baseline Bind/Prevent → constitution |

## Required sections (when file exists)

| Section | Content |
|---------|---------|
| **Human brief** | Which tech ADRs matter for review now |
| **ADRs** | Decision-lite entries with ids `ADR-n` — `skills/rr-planner/refs/decision-lite.md` |
| **Deferred** | Postponed tech choices |
| **Inherited** | Tech constraints from Discover / constitution cites |

Product-shaped Bind/Prevent/Rule that used to live here as “spine” → **migrate to constitution** (`--optimize` rename/refile — AskQuestion first).

Write Human brief last. Persist only after `compose-prose` → `s-humanize`.

## Id convention

- Technical decisions: **`ADR-n`** only under architecture / `adrs/`
- Product feature deltas: **`DEC-n`** or feature-scoped revs — never `ADR-*`

## Rev / draft

Dual-read `architecture_rev` during transition; prefer `constitution_rev` for standing-law pins once constitution-primary. Draft rev OK; draft ≠ missing Decision/Effort drivers on selected capabilities.

## Done-when

- [ ] File contains tech ADRs only (or is absent / stub pointing to constitution)
- No product UX baseline catalog
- No silent combined constitution+architecture mint under `constitution-primary`
