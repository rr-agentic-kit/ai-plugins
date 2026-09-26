# Test lane — severity triage

**Audience:** **s-review** test lane assess; Challenge for test lane.

**Shared schema:** `s-review/refs/severity-triage.md`.

**Rubric:** [shared-heuristics.md](shared-heuristics.md), [test-types.md](test-types.md).

## Challengeable rows

Non-ADEQUATE: **MISSING**, **NON-COMPLIANT**, **OVER-TESTED**, **UNCLEAR**.

| Class | Signals | On uncertainty |
|-------|---------|----------------|
| **Hard** | **MISSING**; **NON-COMPLIANT** with Critical/Major smell; goal/regression/boundary gaps | **MUST NOT** demote alone — `keep` with `uncertain-hard` |
| **Soft** | **UNCLEAR**; **OVER-TESTED**; Minor-only **NON-COMPLIANT** | **MUST demote** when criteria unclear |

**Blockers** for fix/plan/POST = rows that survive emit gate + Challenge (**kept** only).

### Hard MISSING — soft-fixture ADEQUATE close (anti-trigger)

**MUST NOT** demote **MISSING** → Soft / Suggestion, and **MUST NOT** treat coverage as ADEQUATE / scope `pass`, when:

- Brief acceptance or regression signals for extract, install, refuse, replace, or env-detection are evidenced **only** by soft fixtures that fail **Production fidelity and predicate isolation** probes in [shared-heuristics.md](shared-heuristics.md)
- Brief acceptance for **CLI self-replace / upgrade / install-refresh** is evidenced **only** by in-module unit helpers (no hermetic spawn of the shipped entry as process under test) — see **CLI process-under-test fidelity** in [shared-heuristics.md](shared-heuristics.md)
- Composite classifier tests would still pass if an acceptance-critical prefix/reason were removed
- Writability/replace or shared-helper predicates named by production/brief are untested

On uncertainty for these rows: **`keep` with `uncertain-hard`** — same as other Hard MISSING.

## Challenge

**When:** Any challengeable row before plan, **`--ci`** POST, or treating assess as final.

**Read:** this ref + cited heuristic rows. Persist sidecar **`REVIEW_DIR/test-assess-challenge.md`** (or `test-assess-<chunk>-challenge.md`). Paths: `s-review/refs/artifacts.md`.

Planner and **`--ci`** POST use **kept** rows only.
