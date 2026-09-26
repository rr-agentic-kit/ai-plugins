# Sequencing safeguards

**Audience:** L1 `depends_on` and L2 reorder checks. Primary failure mode: **wrong order** when docs and code disagree.

## Posture table

Canonical tokens (persist on summary / session): `greenfield` | `brownfield` | `docs_ahead` | `conflict`.

| Token | Detect | Sequencing rule |
|-------|--------|-----------------|
| `greenfield` | No/minimal application code for pinned capabilities | Foundations (module/skeleton, contracts, migrations) → capability atoms → wiring/UI. Never schedule “integrate with X” before X exists in tree or as an earlier task. Prefer first real seam over doc-only prep. |
| `brownfield` | Code implements behavior not in Plan/ADRs (code ahead of docs) | **Code wins for mechanism discovery** — reverse-derive tech ADRs and steps from live paths/symbols; mark `doc_drift:` on summary; do not invent a parallel greenfield redesign. Sequence against actual call graph. |
| `docs_ahead` | Kernel + deltas clear; code absent for that surface | Follow docs/ADR order; cite planned paths; first tasks may mint files. |
| `conflict` | Code and docs contradict on mechanism | Stop or AskQuestion: adopt code (update ADR) vs adopt docs (task rewrites code). Do not silently average. Text-mode: same options. |

## DAG rules

- L1 `depends_on` must be a **DAG** of global task ids — refuse cycles.
- **Cycle probe (deterministic):** DFS each node with a recursion stack; on back-edge emit `FAIL` + the cycle path (ids only). No cycle → `PASS`. Do not invent alternate graph libraries; do not dump the full adjacency list into chat — emit only PASS or FAIL+cycle.
- L2 may split/reorder only by rewriting summary + reallocating **not-yet-detailed** ids.
- Never renumber committed `detailed` tasks without an explicit migrate note on the summary.

## Re-check

After each L2 write, re-apply the posture row. If a new conflict appears, pause — do not continue inventing order.
