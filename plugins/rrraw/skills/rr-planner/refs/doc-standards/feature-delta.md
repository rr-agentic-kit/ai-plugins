# feature-delta

**Audience: dual** — `refs/planning/doc-standards/dual-audience.md`  
**Owner:** Per-feature product-delta vs standing constitution (OpenSpec-style) — mechanism, Effort drivers, UX-shape. Uses `skills/rr-planner/refs/decision-lite.md`.

**Path:** `docs/rr/{track}/plan/deltas/<feature-id>.md`  
**Load when:** Same-sitting dual-lens for a scored feature; slice freeze pins; research/challenge when load-bearing.

**Does not:** Restate `constitution.md` or tech ADR catalogs. Does not shrink the PRD requirement table. Does not require hi-fi wireframes. Does not use `ADR-*` ids (reserved for tech).

## Required sections

| Section | Content |
|---------|---------|
| **Human brief** | Context + Decision in plain language up front — why this delta, what was chosen, feedback needed; no new IDs |
| **Feature** | Feature id + title (e.g. `PRD-3`) |
| **Context** | Why this delta exists now |
| **Decision** | Mechanism/integration choice for this feature |
| **Effort drivers** | **Required when the feature has `_effort_:`** — 2–5 bullets naming what made Effort = N (tech and/or UX) |
| **UX-shape** | Interaction pattern, surfaces/flow, **cost-relevant states** — or explicit out-of-slice. Pure backend: `n/a` + reason |
| **Consequences** | Follow-ons |
| **Rejections** | Alternatives rejected (`skills/rr-planner/refs/decision-lite.md`); optional one-line effort hint per option |
| **Integration points** | APIs / events / UI boundaries touched |
| **Data-model delta** | Entities/fields changed vs standing law |
| **Refs** | Pointers to constitution INDEX + cited tech ADRs + requirement leaves — no copy |

Ids: `DEC-n` or feature-scoped revs — **not** `ADR-*`.

Human brief restates Context+Decision for reviewers. Persist only after `compose-prose` → `s-humanize`.

## Rules

1. Reference standing constitution (+ cited tech ADR) — **never restate** them.
2. Once accepted → supersede-only (new rev or superseding file section).
3. Product AC stays on PRD (WWAS); delta owns mechanism + Effort drivers + UX-shape.
4. Selecting a slice pins `delta_paths` in `execute-slice.yaml` without deleting deferred requirements.
5. Refuse `_effort_:` unless this delta (or constitution/tech entry for the capability) cites **Effort drivers** in the same sitting (`skills/rr-planner/refs/system-design.md`).

## Done-when

- [ ] Human brief is reviewable without the rest of the delta
- Context / Decision / Consequences present
- Effort drivers present when feature has `_effort_:`
- UX-shape present for UI-facing; `n/a` + reason for pure backend
- Constitution/tech cited, not copied
- Supersede path respected after accept
- No `ADR-*` on product deltas
