# Tech decisions (lazy ADR)

**Audience:** Tech-decision gate (before/alongside L1–L2). Product DEC/constitution stay **rr-planner**.

## Inventory (always)

List **technical** decision *topics* needed for the slice: stack, integration, data model, migration, boundaries. Record on `task-summary.md` as `pending_tech`:

| Field | Meaning |
|-------|---------|
| `topic` | Short decision name |
| `blocked_task_ids` | Global ids that cannot detail without the decision |
| `status` | `pending` \| `forced` \| `resolved` |

## When to persist `ADR-n`

**Do not** mint/persist until the decision **must** be made — i.e. when L1 ordering or an L2 task would otherwise invent mechanism, or when two irreversible options block that step.

When forced:

1. Write/revise `ADR-n` under plan `architecture.md` and/or `adrs/` per Plan `skills/rr-planner/refs/doc-standards/architecture.md` + decision-lite
2. Brownfield: reverse-derive from live code; cite paths/symbols
3. Cite the ADR from blocked task files (`adr_refs`)
4. Update `pending_tech` → `resolved`

## AskQuestion

Only for load-bearing **irreversible** forks. Prefer AskQuestion; text-mode lists the same options and continues without stalling.

## Ownership

| Layer | Owner |
|-------|--------|
| Product constitution / DEC / UX-shape | **rr-planner** |
| Build-blocking tech ADR gaps for this slice | **s-prepare** (lazy mint) |
| Implement | **s-coder** (later) |

## Non-goals

- Pre-pass dump of every possible ADR
- Product mechanism inventing (belongs in deltas)
- Opening PRs
