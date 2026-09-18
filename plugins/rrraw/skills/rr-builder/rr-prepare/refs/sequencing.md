# Sequencing safeguards

**Audience:** L1 `depends_on` and L2 reorder checks. Primary failure mode: **wrong order** when docs and code disagree.

## Posture table

| Posture | Detect | Sequencing rule |
|---------|--------|-----------------|
| **Greenfield** | No/minimal application code for pinned capabilities | Foundations (module/skeleton, contracts, migrations) → capability atoms → wiring/UI. Never schedule “integrate with X” before X exists in tree or as an earlier task. Prefer first real seam over doc-only prep. |
| **Brownfield / code ahead of docs** | Code implements behavior not in Plan/ADRs | **Code wins for mechanism discovery** — reverse-derive tech ADRs and steps from live paths/symbols; mark `doc_drift:` on summary; do not invent a parallel greenfield redesign. Sequence against actual call graph. |
| **Docs ahead of code** | Kernel + deltas clear; code absent for that surface | Follow docs/ADR order; cite planned paths; first tasks may mint files. |
| **Conflict** | Code and docs contradict on mechanism | Stop or AskQuestion: adopt code (update ADR) vs adopt docs (task rewrites code). Do not silently average. Text-mode: same options. |

## DAG rules

- L1 `depends_on` must be a **DAG** of global task ids — refuse cycles.
- L2 may split/reorder only by rewriting summary + reallocating **not-yet-detailed** ids.
- Never renumber committed `detailed` tasks without an explicit migrate note on the summary.

## Re-check

After each L2 write, re-apply the posture row. If a new conflict appears, pause — do not continue inventing order.
