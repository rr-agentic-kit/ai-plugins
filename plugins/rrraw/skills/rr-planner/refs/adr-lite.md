# adr-lite

**Owner:** Lightweight ADR rules for standing architecture and feature deltas. Accepted decisions are append-only / supersede-only.

**Load when:** Writing or revising `docs/plan/architecture.md`, `constitution.md`, or `docs/plan/deltas/<feature-id>.md`.

**Does not:** Replace the decision-ledger `r-*` graph. Does not invent a second audit trail (no BMAD memlog).

## Record shape (minimum)

| Field | Required | Notes |
|-------|----------|-------|
| **Context** | yes | Why a decision is needed now |
| **Decision** | yes | The choice in one or two sentences |
| **Consequences** | yes | What follows (good and bad) |
| **Rejections** | yes when alternatives existed | Options considered and why rejected — stop re-proposal loops |
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
- Rejections recorded when alternatives were debated
- No silent edit of an accepted ADR
