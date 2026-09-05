# feature-delta

**Owner:** Per-feature change vs standing spine (OpenSpec-style delta mindset).

**Path:** `docs/plan/deltas/<feature-id>.md`  
**Load when:** Same-sitting architecture for a scored feature; slice freeze pins.

**Does not:** Restate `architecture.md`. Does not shrink the PRD requirement table.

## Required sections

| Section | Content |
|---------|---------|
| **Feature** | Feature id + title (e.g. `PRD-3`) |
| **Context** | Why this delta exists now |
| **Decision** | Mechanism/integration choice for this feature |
| **Consequences** | Follow-ons |
| **Rejections** | Alternatives rejected (`skills/rr-planner/refs/adr-lite.md`) |
| **Integration points** | APIs / events / UI boundaries touched |
| **Data-model delta** | Entities/fields changed vs spine |
| **Refs** | Pointers to spine invariants + requirement leaves — no spine copy |

## Rules

1. Reference standing architecture — **never restate** it.
2. Once accepted → supersede-only (new rev or superseding file section).
3. Product AC stays on PRD (WWAS); delta owns mechanism.
4. Selecting a slice pins `delta_paths` in `execute-slice.yaml` without deleting deferred requirements.

## Done-when

- Context / Decision / Consequences present
- Spine cited, not copied
- Supersede path respected after accept
