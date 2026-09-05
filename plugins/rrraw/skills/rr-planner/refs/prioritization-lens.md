# prioritization-lens

**Owner:** Decision table for Plan scoring frameworks. Default RICE (features) / RIC (stories); alternate lenses on demand.

**Load when:** Scoring features/stories, or founder asks for a different prioritization frame.

**Does not:** Run every framework. MoSCoW stays Discover-only. Sprint capacity/velocity are out of scope.

## Default

| Surface | Method | Notes |
|---------|--------|-------|
| Features | **RICE** | Reach, Impact, Confidence, Effort — factors only; composed score not stored |
| Stories | **RIC** | No Effort |
| Goals | `primary` / `support` | Not RICE |
| Requirement leaves | **P1 / P2 / P3** | Priority inside a feature’s full set — `refs/planning/doc-standards/item-schema.md` |

Effort is real only with same-sitting architecture ([plan-interview.md](plan-interview.md), [system-design.md](system-design.md)).

## On-demand lenses (pick one)

| Lens | When | Do not |
|------|------|--------|
| **ICE** | Quick triage before full RICE | Use as permanent backlog score |
| **Opportunity Score** | Prioritizing *problems* / opportunities (rare in Plan; usually Discover) | Re-open market sizing |
| **Kano** | Explicit satisfaction-vs-absence debate on a capability | Replace RICE on the whole backlog |

Never run all frameworks in one pass. Ask once which lens if the founder rejects RICE/RIC.

## Anti-patterns

- Shrinking the requirement table to match what ships — use `_status_:` selection instead
- Fibonacci as sprint capacity theater
- P0 / MoSCoW on PRD
- Effort without architecture — [system-design.md](system-design.md)

## Done-when

- Default RICE/RIC applied unless an on-demand lens was explicitly chosen
- P1–P3 only on requirement leaves
- Effort gated by architecture pass
