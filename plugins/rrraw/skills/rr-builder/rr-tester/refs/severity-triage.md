# Test lane — severity triage

**Audience:** **rr-review** test lane assess; Challenge for test lane.

**Shared schema:** [rr-review/refs/severity-triage.md](../../rr-review/refs/severity-triage.md).

**Rubric:** [shared-heuristics.md](shared-heuristics.md), [test-types.md](test-types.md).

## Challengeable rows

Non-ADEQUATE: **MISSING**, **NON-COMPLIANT**, **OVER-TESTED**, **UNCLEAR**.

| Class | Signals | On uncertainty |
|-------|---------|----------------|
| **Hard** | **MISSING**; **NON-COMPLIANT** with Critical/Major smell; goal/regression/boundary gaps | **MUST NOT** demote alone — `keep` with `uncertain-hard` |
| **Soft** | **UNCLEAR**; **OVER-TESTED**; Minor-only **NON-COMPLIANT** | **MUST demote** when criteria unclear |

**Blockers** for fix/plan/POST = rows that survive emit gate + Challenge (**kept** only).

## Challenge

**When:** Any challengeable row before plan, **`--ci`** POST, or treating assess as final.

**Read:** this ref + cited heuristic rows. Persist appendix under **`REVIEW_DIR/test/assess/`**.

Planner and **`--ci`** POST use **kept** rows only.
