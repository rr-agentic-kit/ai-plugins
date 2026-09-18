# Compatibility gate (L2 done-when)

**Audience:** Before marking a task `detailed` on the summary.

## PASS when all true

1. **Requirements mapped** — `requirement_ids` (or explicit prep unlock) cite pinned kernel requirements.
2. **Mechanism cited** — tech ADR and/or concrete paths/symbols so implementers do not invent stack/integration.
3. **Constitution intact** — Obligations do not violate standing Bind/Prevent/Rule from constitution INDEX.
4. **Non-hollow** — Steps are actionable; not a single “implement X” with no mechanism.

## FAIL

| Signal | Action |
|--------|--------|
| Hollow “implement X” without mechanism | Keep `pending`; force tech gate or deepen steps |
| Missing requirement map | Fix frontmatter / Goal |
| Invented product intent not in pins/deltas | Stop — route product gap to **rr-planner** |
| Violates constitution | Rewrite Obligations / Non-goals |

On FAIL: do not mark `detailed`; do not advance to next L2 until fixed or human stops the run.
