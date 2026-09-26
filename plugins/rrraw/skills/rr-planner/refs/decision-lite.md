# decision-lite

**Owner:** Lightweight decision record shape for standing constitution shards, tech ADRs, and feature deltas. Accepted decisions are append-only / supersede-only.

**Load when:** Writing or revising `constitution.md` / `constitution/invariants/`, `architecture.md` / `adrs/`, or `deltas/<feature-id>.md`.

**Does not:** Replace the decision-ledger `r-*` graph. Does not invent a second audit trail. Does not mandate a full effort matrix / SWOT on every leaf. Does not put product deltas under `ADR-*` ids.

## Record shape (minimum)

| Field | Required | Notes |
|-------|----------|-------|
| **Context** | yes | Why a decision is needed now |
| **Decision** | yes | The choice in one or two sentences |
| **Consequences** | yes | What follows (good and bad) |
| **Rejections** | yes when alternatives existed | Options considered and why rejected — stop re-proposal loops. Optional one-line **effort hint** per option when Effort would differ |
| **Effort drivers** | when feature has `_effort_:` | 2–5 bullets naming cost drivers — [feature-delta.md](doc-standards/feature-delta.md) |
| **UX-shape** | UI-facing features before freeze; else `n/a` + reason | Interaction pattern / flow / cost-relevant states — not pixels |
| **Integration points** | when relevant | Boundaries touched |
| **Data-model delta** | when relevant | Schema/entity change vs standing law |

Feature deltas: [doc-standards/feature-delta.md](doc-standards/feature-delta.md). Standing law: [doc-standards/constitution.md](doc-standards/constitution.md). Tech ADRs: [doc-standards/architecture.md](doc-standards/architecture.md).

## Supersede rules

| Event | Rule |
|-------|------|
| Accepted decision | Do **not** silently edit the accepted text |
| Change of mind | New id / new delta revision that **supersedes** the prior; mark old as superseded |
| Rejection | Record in Rejections so agents do not re-propose |
| Draft | Editable until accepted; once accepted → supersede path |

## Id convention

| Altitude | Id |
|----------|-----|
| Tech under architecture / `adrs/` | **`ADR-n`** (reserved) |
| Product feature-delta | File = `deltas/<feature-id>.md`; internal **`DEC-n`** or date/`rev: n` supersede pointers — **not** `ADR-*` |
| Constitution invariant shard | Pointer from INDEX; optional `DEC-n` in shard body |

## Done-when

- Context / Decision / Consequences present
- Rejections recorded when alternatives were debated
- Effort drivers + UX-shape present where feature-delta rules require them
- No silent edit of an accepted decision
- Product deltas do not use `ADR-*`
