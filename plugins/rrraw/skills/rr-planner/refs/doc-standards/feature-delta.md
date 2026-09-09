# feature-delta

**Audience: dual** — `refs/planning/doc-standards/dual-audience.md`  
**Owner:** Per-feature change vs standing spine (OpenSpec-style delta mindset) — mechanism, Effort drivers, UX-shape.

**Path:** `docs/rr/{track}/plan/deltas/<feature-id>.md`  
**Load when:** Same-sitting architecture for a scored feature; slice freeze pins.

**Does not:** Restate `architecture.md`. Does not shrink the PRD requirement table. Does not require hi-fi wireframes.

## Required sections

| Section | Content |
|---------|---------|
| **Human brief** | Context + Decision in plain language up front — why this delta, what was chosen, feedback needed; no new IDs |
| **Feature** | Feature id + title (e.g. `PRD-3`) |
| **Context** | Why this delta exists now |
| **Decision** | Mechanism/integration choice for this feature |
| **Effort drivers** | **Required when the feature has `_effort_:`** — 2–5 bullets naming what made Effort = N (tech and/or UX; e.g. “multi-step wizard + new payment webhook”) |
| **UX-shape** | Interaction pattern, surfaces/flow, **cost-relevant states** decided on purpose (empty / error / permission — or explicit out-of-slice). Wireframe = optional low-fi sketch notes, never pixel DoR. UI-facing selected features: required before freeze. Pure backend: `n/a` + reason |
| **Consequences** | Follow-ons |
| **Rejections** | Alternatives rejected (`skills/rr-planner/refs/adr-lite.md`); optional one-line effort hint per option |
| **Integration points** | APIs / events / UI boundaries touched |
| **Data-model delta** | Entities/fields changed vs spine |
| **Refs** | Pointers to spine invariants + requirement leaves — no spine copy |

Human brief restates Context+Decision for reviewers who will not dig into ADR-lite fields. Write brief last from locked facts (or outline then refresh) — no invented claims. Persist only after `compose-prose` → `rr-humanize`.

## Rules

1. Reference standing architecture — **never restate** it.
2. Once accepted → supersede-only (new rev or superseding file section).
3. Product AC stays on PRD (WWAS); delta owns mechanism + Effort drivers + UX-shape.
4. Selecting a slice pins `delta_paths` in `execute-slice.yaml` without deleting deferred requirements.
5. Refuse `_effort_:` unless this delta (or spine entry for the capability) cites **Effort drivers** in the same sitting (`skills/rr-planner/refs/system-design.md`).

## Done-when

- [ ] Human brief is reviewable without the rest of the delta (Context+Decision plain language)
- Context / Decision / Consequences present
- Effort drivers present when feature has `_effort_:`
- UX-shape present for UI-facing; `n/a` + reason for pure backend
- Spine cited, not copied
- Supersede path respected after accept
