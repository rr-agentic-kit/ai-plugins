# compose-prose

**Owner:** Mandatory humanize gate before cascade `.md` (and human-facing session artifacts) hit disk. **Orchestrating skill owns this** — the compose agent does not.

**Load when:** After compose agent returns a draft receipt for `executive-summary` / `mrd` / `brd`, or when persisting conditional session markdown (`assumptions.md`, `opportunity-tree.md`, `interview-synthesis.md`, `pretotype-brief.md`, challenge report prose). Plan reuses the same gate for PRD writes.

**Does not:** change item IDs, frontmatter contracts, MoSCoW/Kano ranks, or ledger facts. Meaning lock to ledger/items is absolute.

## Pipeline

```
compose agent draft (meaning lock)
        │
        ▼
skill: compose-prose.md
        │
        ├─ first write  → rr-humanize generate
        └─ re-compose   → rr-humanize rewrite
        │
        ▼
claim check → persist .md
```

1. **Compose agent emits draft** — facts locked to ledger / `items.json` / level notes. Agent returns slim receipt; it does **not** call humanize.
2. **Skill loads** [`skills/docs/rr-humanize/`](../../docs/rr-humanize/SKILL.md):
   - **generate** on first write of that stem/artifact — [refs/generate.md](../../docs/rr-humanize/refs/generate.md)
   - **rewrite** on re-compose / patch prose — [refs/rewrite.md](../../docs/rr-humanize/refs/rewrite.md)
   - Always apply [refs/readability.md](../../docs/rr-humanize/refs/readability.md) during reshape.
3. **CLI budget** (per persist):
   - generate ≤ **1** `scan`
   - rewrite ≤ **2** (`scan`, optional `apply-safe`)
   - Paths relative to plugin root, e.g. `python3 skills/docs/rr-humanize/scripts/cli.py scan …` (follow humanize SKILL for exact invocation).
4. **Claim check** — humanize must **not** invent TAM, metrics, Musts, stakeholders, or premises. Every sentence traces to draft/ledger/items. Structural IDs, YAML frontmatter, and item blocks are **out of scope** for lexicon wipe — prose sections only.
5. **Persist** only after claim check passes. On failure → fix prose or AskQuestion; do not write invented specificity.

## Machine files — skip humanize

| File | Reason |
|------|--------|
| `business-case.yaml` | Machine handoff contract |
| `items.json` | Item graph |
| `decision-ledger.yaml` | Reason graph |
| `session-state.json` | Checkpoint |
| `status.yaml` | Skill-owned pins |
| `{level}.notes.yaml` | Sidecar parking |
| `raw-history/*` | Audit log |

Do not run scan/reshape on these.

## Prose scope

| In scope | Out of scope for lexicon / readability wipe |
|----------|-----------------------------------------------|
| Narrative sections, overviews, appendices | `{DOC}-n.m` ids, `_key_:` lines, parent pointers |
| Challenge report prose body | Frontmatter keys (`doc_rev`, `depth`, …) |
| Session artifacts listed above | Rank enums, rationale id tokens |

Preserve hedges that encode real uncertainty (`hold`, `vague`) — firm tone must not delete honest unknowns ([rr-humanize rewrite meaning lock](../../docs/rr-humanize/refs/rewrite.md)).

## Ownership split

| Actor | Responsibility |
|-------|----------------|
| Compose agent | Draft meaning-locked content + receipt |
| Skill (Discover / Plan) | Load this ref; run humanize; claim check; write files; stamp status |
| Validator | Shape/IDs — not prose quality |

If compose agent is asked to "humanize" → refuse; skill runs this gate.

## Failure handling

| Situation | Action |
|-----------|--------|
| Scan/CLI unavailable | Do not silently skip — report blocker; persist only if user accepts raw draft risk (log decision) |
| Claim check fails (invented TAM/metric/Must) | Strip invention; re-check; do not freeze on poisoned prose |
| Budget exhausted with remaining judgment hits | One LLM reshape without extra CLI; then persist or AskQuestion |
| Machine file mistaken for prose | Skip humanize |

## Done-when

- Humanize path selected (generate vs rewrite)
- CLI budget respected
- Claim check clean
- Cascade/session `.md` written; machine files untouched by humanize
- Compose agent never invoked humanize itself
