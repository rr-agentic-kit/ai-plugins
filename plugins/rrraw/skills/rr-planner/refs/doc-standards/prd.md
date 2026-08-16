# prd (Product Requirements Document)

**Cascade level:** 4  
**Inherits from:** exec-summary + MRD + BRD  
**Narrows to:** product capabilities, user outcomes, and priorities  
**Priority method:** MoSCoW on goals, stories, and features — [item-schema.md](item-schema.md)  
**Panel seats:** Head of product + UX + domain practitioner (advisory) — [expert-panel.md](../expert-panel.md)  
**Blind-spots (stage-exit):** Scan only the prd row in [blind-spots.md](../blind-spots.md) (`in_scope` + `inherit_check`). Do not copy the taxonomy here.

## Purpose

Define what the product will do to achieve business objectives. Feature-level thinking starts here, not before.

## Required sections

| Section | Content | Items |
|---------|---------|-------|
| **Product overview** | One-paragraph product description tied to vision | Prose (unnumbered) |
| **Goals** | Product goals mapped to BRD objectives | Ranked leaves |
| **User personas** | Primary personas with goals, pain points, context | Unranked leaves (`_moscow_: —`) |
| **User stories / outcomes** | Outcome-oriented capabilities (not implementation) | Ranked leaves |
| **Features** | Capabilities that deliver stories | Ranked leaves; MoSCoW *legend* from [project-posture.md](../project-posture.md) — not a hardcoded Must=MVP |
| **Out of scope** | Product-level exclusions (inherits exec non-goals) | Ranked leaves; `Won't` |
| **Release phasing** | Horizon buckets for this session | Prose derived from MoSCoW + posture legend — do not store a second rank; **state which legend was used** |

Prefix `PRD`. Product scoping, not implementation. Do not add `if_wrong` or P0/P1/P2. No `horizon:` field on items. Cut-pass: [project-posture.md](../project-posture.md).

PRD “delivered” is derived from Must FRD children (`build: done`). Do not store build status on PRD items.

## Extraction method (discovery)

1. For each BRD objective, ask "what product capability delivers this?"
2. Write user stories as outcomes: "As [persona], I can [outcome] so that [business value]."
3. Challenge feature requests against exec-summary non-goals. Under `existing`, shipped behavior is already a constraint — do not restate it as a Must feature to build.
4. Prioritize with MoSCoW — Must/Should/Could/Won’t using the **posture legend**; force split if a story hides multiple outcomes.
5. Run the **cut-pass** once after MoSCoW, before Gate 6 freeze ([project-posture.md](../project-posture.md)). `unsigned`: can the Must slice move an ES metric? `signed_v1`: do not ask "is this MVP?"; new Must → `scope_change` or reject.
6. Write release-phasing prose from the legend (Should+Could = v1+ when unsigned; Won't = never, not later).

## Traceability

- Cross-doc `parent:` is a `BRD-*` id (usually an objective). Same-doc nest: `PRD-n` → `PRD-n.m`.
- Each goal walks to a BRD objective. Each story walks to a goal (and names a persona in the body).
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

- [ ] Product overview links to exec-summary vision
- [ ] Every BRD objective has at least one product goal
- [ ] Personas defined with goals and pain points
- [ ] User stories are outcome-oriented (no implementation detail)
- [ ] Goals, stories, and features have `_moscow_` + `_rationale_`; ranks match the posture legend (Must is not automatically MVP)
- [ ] Release-phasing prose states which legend was used
- [ ] Out-of-scope items documented as `Won't` (never — not "later")
- [ ] Items use `PRD-{n}` / `PRD-{n.m}` per item-schema; compounds split into container + leaves
- [ ] No feature contradicts exec-summary non-goals or BRD business rules
