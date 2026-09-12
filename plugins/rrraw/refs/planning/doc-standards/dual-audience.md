# dual-audience

**Owner:** Shared reading contract for every cascade / standing Plan stem humans review for feedback (ES, MRD, BRD, PRD, architecture, constitution, feature-delta). ID grammar lives in [item-schema.md](item-schema.md) (AI-only) — this ref does not soften those rules.

**Load when:** Authoring or composing any cascade `.md` (`executive-summary` … `prd`), standing spine / constitution / feature delta, or running `compose-prose` before persist.

**Does not:** Change item schema, validator codes, or ledger facts. Does not replace `compose-prose.md` / `rr-humanize` — it obligates them.

## Audiences

| Audience | Needs |
|----------|--------|
| **Human** | Real feedback without decoding MoSCoW/RICE metadata or the item graph |
| **AI + validators** | Stable IDs, `_key_:` leaves, `items.json` drift checks, Item index |

Both consume the **same file**. Dual audience is a template obligation, not a sidecar.

## Reading order

After H1:

1. **Human brief** (required — first body section)
2. Existing prose sections (per level doc-standard)
3. Ranked items (heading + `_key_:` + `>` body)
4. **Item index** (last)

## Human brief

Unnumbered prose. Roughly ½–1 page max. No new IDs. Must be understandable without reading the item graph.

| Include | Exclude |
|---------|---------|
| Decision / ask for the reader | New ranked claims or fake metrics |
| What changed since last rev (or “first draft”) | MoSCoW/RICE/Kano laundry lists |
| Top risks / holds that block feedback | Invented TAM, Musts, stakeholders |
| What feedback is needed now | Lexicon that only makes sense with `_key_:` lines |

**SoT:** Item graph + ledger remain source of truth for ranked claims. Brief must not invent facts — claim-check against `level_facts` / ledger / `items.json`. Write brief **last** from locked facts (or outline first, then refresh after mint) so it cannot drift ahead of the graph.

## Always humanize

Every cascade / session `.md` prose persist runs `skills/rr-discovery/refs/compose-prose.md` → `rr-humanize` (generate on first write; rewrite on re-compose). Machine YAML/JSON still skip. Default cascade prose register: `active` + `plain`.

## Leaf bodies

`>` blockquote bodies are **in scope** for readability / lexicon reshape. IDs and `_key_:` lines stay untouched. Prefer readable shalls — do not wipe rank enums or rationale tokens.

## Pointers

| Ref | Role |
|-----|------|
| [item-schema.md](item-schema.md) | AI-only — IDs, `_key_:`, index grammar |
| Level `refs/doc-standards/<stem>.md` (ES/MRD/BRD/PRD + standing Plan stems) | Dual-audience templates — Human brief + required sections |
| `skills/rr-discovery/refs/compose-prose.md` | Persist gate + claim check |
| `refs/planning/output-formats.md` | Markdown layout |
