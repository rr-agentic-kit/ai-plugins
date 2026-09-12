# adr-lite

**Owner:** Lightweight ADR rules for standing architecture and feature deltas. Accepted decisions are append-only / supersede-only.

**Load when:** Writing or revising `docs/rr/{track}/plan/architecture.md`, `constitution.md`, or `docs/rr/{track}/plan/deltas/<feature-id>.md`.

**Does not:** Replace the decision-ledger `r-*` graph. Does not invent a second audit trail (no BMAD memlog). Does not mandate a full effort matrix / SWOT on every leaf.

## Record shape (minimum)

| Field | Required | Notes |
|-------|----------|-------|
| **Context** | yes | Why a decision is needed now |
| **Decision** | yes | The choice in one or two sentences |
| **Consequences** | yes | What follows (good and bad) |
| **Rejections** | yes when alternatives existed | Options considered and why rejected — stop re-proposal loops. Optional one-line **effort hint** per option when Effort would differ (no mandatory matrix) |
| **Effort drivers** | when feature has `_effort_:` | 2–5 bullets naming cost drivers — [feature-delta.md](doc-standards/feature-delta.md) |
| **UX-shape** | UI-facing features before freeze; else `n/a` + reason | Interaction pattern / flow / cost-relevant states — not pixels |
| **Integration points** | when relevant | Boundaries touched |
| **Data-model delta** | when relevant | Schema/entity change vs standing spine |

Feature deltas: [doc-standards/feature-delta.md](doc-standards/feature-delta.md). Spine: [doc-standards/architecture.md](doc-standards/architecture.md).

## Supersede rules

| Event | Rule |
|-------|------|
| Accepted decision | Do **not** silently edit the accepted text |
| Change of mind | New id / new delta revision that **supersedes** the prior; mark old as superseded |
| Rejection | Record in Rejections so agents do not re-propose |
| Draft spine | Editable until accepted; once accepted → supersede path |

## Id convention

- Spine decisions: `ADR-n` (or section anchors) inside `architecture.md`
- Feature deltas: file = `deltas/<feature-id>.md`; internal supersede pointers by date or `rev: n`

## Done-when

- Context / Decision / Consequences present
- Rejections recorded when alternatives were debated (optional effort hint per option when ranking differed)
- Effort drivers + UX-shape present where feature-delta rules require them
- No silent edit of an accepted ADR
