# Capability atom (task grain)

**Audience:** L1 decomposition. Between a single config toggle and a full PRD leaf.

## Target

Smallest chunk that delivers **observable product/business value** (or a coherent prep that unlocks value) — typically one capability facet or **1–2 tightly coupled requirements** on the same surface.

## Pass / fail

| Verdict | Example |
|---------|---------|
| **PASS** | “Guest checkout: persist cart → order” (one surface, observable) |
| **PASS** | “Add migration + repository seam for Order” (prep that unlocks value) |
| **FAIL — too small** | Pure rename; unrelated drive-by cleanup; toggle flip with no user/system outcome |
| **FAIL — too large** | Entire parent feature / multi-surface epic → **split before L2** |

## Rules

- Map each atom to `requirement_ids` from kernel pins (or explicit prep unlocking those ids).
- If an atom needs more than one PR to review safely, keep one task and let L3 split PRs — do not inflate grain solely for PR size.
- Foundations allowed when posture is greenfield and later atoms depend on them.
