# prd (Product Requirements Document)

**Cascade level:** 4  
**Inherits from:** exec-summary + MRD + BRD  
**Narrows to:** product capabilities, user outcomes, and scored backlog  
**Priority method:** RICE on features; RIC on stories; `primary`/`support` on goals — [item-schema.md](item-schema.md)  
**Panel seats:** Head of product + UX + domain practitioner (advisory) — [expert-panel.md](../expert-panel.md)  
**Blind-spots (stage-exit):** Scan only the prd row in [blind-spots.md](../blind-spots.md) (`in_scope` + `inherit_check`). Do not copy the taxonomy here.

## Purpose

Define what the product will do to achieve business objectives. Feature-level thinking starts here, not before. PRD is a **scored backlog**, not a cut-pass or release plan.

## PRD-shape reflection (T8-20..26)

Before minting structure (and earlier at discovery when scope mode is unclear), recommend `prd_shape` + `scope_mode` from the factor table below. User confirms; persist in **both** `session_state.project_posture` and the PRD **Shape** section.

| Factor | Tips `story_led` / `discovery` | Tips `feature_led` / `closed` |
|--------|-------------------------------|------------------------------|
| **Scope certainty** | Unknown market-minimum; exploring fit | Known MVP contract; packaging capabilities |
| Primary audience of the doc | Discovery / outcome alignment | Spec for delivery / capability buyers |
| Market shape | B2C, persona-heavy | B2B, buyer≠user |
| What gets prioritized | Outcomes / JTBD first | Capabilities / RICE-on-features first |
| WIP style | Stories before capabilities named | Features first; stories as usage angles |
| Downstream need | Stays PM-only; tech skill later | Needs engineering contract sooner |
| NFR criticality | Few product-level NFRs | Several NFRs are product commitments on PRD |

**Output:** `prd_shape: story_led | feature_led | hybrid` + `scope_mode: discovery | closed`. Revisit only on explicit user change or objective shift (T10-8).

## Required sections

| Section | Content | Items |
|---------|---------|-------|
| **Shape** | Confirmed `prd_shape` + `scope_mode` from reflection | Prose (unnumbered) |
| **Product overview** | One-paragraph product description tied to vision | Prose (unnumbered) |
| **Goals** | Product goals mapped to BRD objectives | Ranked leaves; `_goal-type_: primary \| support` |
| **User personas** | Primary personas with goals, pain points, context | Prose (unnumbered); meaningful default for B2C, optional for B2B |
| **User stories / outcomes** | Outcome-oriented capabilities (not implementation) | Ranked leaves; RIC scoring |
| **Features** | Capabilities that deliver stories | Ranked leaves; full RICE scoring |
| **Out of scope** | Product-level exclusions (inherits exec non-goals) | Ranked leaves; no RICE |

Prefix `PRD`. Product scoping, not implementation. Do not add `if_wrong` or P0/P1/P2. No `horizon:` field on items. No MoSCoW. No release phasing. Personas stay a section; stories name a persona in the body (`As [persona]`) — they do not parent to a persona id.

PRD “delivered” is the manual `_status_:` field on PRD leaves (e.g. `delivered`) — set directly by user/dev workflow; not derived from children.

## RICE scoring (T8-1..15)

Persist **factors only** — composed `(R×I×C)/E` score is **not stored** (ordering out of scope).

| Factor | Features | Stories | Values |
|--------|----------|---------|--------|
| **Reach** | ✓ | ✓ | 10–100% of a **named** target — state the denominator (user base, SAM slice, portion of an ES metric, …) |
| **Impact** | ✓ | ✓ | `0.25` Minimal · `0.5` Low · `1` Medium · `2` High · `3` Massive |
| **Confidence** | ✓ | ✓ | `low`→0.5 · `medium`→0.8 · `high`→1.0 |
| **Effort** | ✓ | — | Fibonacci `1, 2, 3, 5, 8, 13` on **features only** |

Stories score **RIC** (no Effort). Features score full **RICE**. Goals use `primary`/`support` only. Out-of-scope items get no RICE factors.

### Story↔feature alignment (T8-16)

After scoring, validate RICE/RIC consistency and adherence to parent feature intent — story angles must align with the feature's stated capability; factors must not be wildly inconsistent across the parent/child pair.

## NFR placement (T8-22)

Circumstantial — some NFRs are product-facing and stay on PRD (stakeholder-visible commitments); mechanism-level detail (integration points, error-handling specifics, AC overflow) routes to `tech.md` ([output-formats.md](../output-formats.md)).

## Extraction method (discovery)

1. Run **PRD-shape reflection** if `prd_shape`/`scope_mode` not yet confirmed; persist to session and Shape section.
2. For each BRD objective, ask "what product capability delivers this?"
3. Write user stories as outcomes: "As [persona], I can [outcome] so that [business value]."
4. Challenge feature requests against exec-summary non-goals and functional deliverables. Under `existing`, shipped behavior is already a constraint — do not restate it as a feature to build.
5. Score features with full RICE; score stories with RIC. In `discovery` mode, incomplete RICE is acceptable on `idea`/`draft` leaves — do not force RICE-complete on every leaf before the backlog shape stabilizes.
6. WIP story without a parent capability → notes/unattached draft until shape rules attach it.
7. Run story↔feature alignment check after scoring passes.

## Traceability (C2-7)

- Cross-doc `parent:` is **≥1 `ES-*` id OR ≥1 `BRD-*` id** (OR, not AND). Allows tech-debt, compliance-from-BRD, and refactor-only backlog items without a direct ES parent.
- Same-doc nest: `PRD-n` → `PRD-n.m`.
- Each goal walks to a BRD objective. Each story walks to a goal (and names a persona from the User personas section in the body).
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

Per-doc bars only. Gate 1, the script, shared success-criteria, and Gate 6 `in_scope` own the rest.

- [ ] Shape section records confirmed `prd_shape` + `scope_mode`
- [ ] Product overview links to exec-summary vision
- [ ] Every BRD objective has at least one product goal
- [ ] User stories are outcome-oriented (fail: implementation detail)
- [ ] Features have RICE factors (or explicit `—` placeholder while `idea`/`draft`)
- [ ] Stories have RIC factors where scored
- [ ] Every PRD item has cross-doc parent ≥1 ES **or** ≥1 BRD
