# feature-delta

**Audience: dual** — `refs/planning/doc-standards/dual-audience.md`  
**Owner:** Per-feature change vs standing spine (OpenSpec-style delta mindset).

**Path:** `docs/plan/deltas/<feature-id>.md`  
**Load when:** Same-sitting architecture for a scored feature; slice freeze pins.

**Does not:** Restate `architecture.md`. Does not shrink the PRD requirement table.

## Required sections

| Section | Content |
|---------|---------|
| **Human brief** | Context + Decision in plain language up front — why this delta, what was chosen, feedback needed; no new IDs |
| **Feature** | Feature id + title (e.g. `PRD-3`) |
| **Context** | Why this delta exists now |
| **Decision** | Mechanism/integration choice for this feature |
| **Consequences** | Follow-ons |
| **Rejections** | Alternatives rejected (`skills/rr-planner/refs/adr-lite.md`) |
| **Integration points** | APIs / events / UI boundaries touched |
| **Data-model delta** | Entities/fields changed vs spine |
| **Refs** | Pointers to spine invariants + requirement leaves — no spine copy |

Human brief restates Context+Decision for reviewers who will not dig into ADR-lite fields. Write brief last from locked facts (or outline then refresh) — no invented claims. Persist only after `compose-prose` → `rr-humanize`.

## Rules

1. Reference standing architecture — **never restate** it.
2. Once accepted → supersede-only (new rev or superseding file section).
3. Product AC stays on PRD (WWAS); delta owns mechanism.
4. Selecting a slice pins `delta_paths` in `execute-slice.yaml` without deleting deferred requirements.

## Done-when

- [ ] Human brief is reviewable without the rest of the delta (Context+Decision plain language)
- Context / Decision / Consequences present
- Spine cited, not copied
- Supersede path respected after accept
