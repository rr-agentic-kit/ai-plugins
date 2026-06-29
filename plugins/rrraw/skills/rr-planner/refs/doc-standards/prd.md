# prd (Product Requirements Document)

**Cascade level:** 4  
**Inherits from:** exec-summary + MRD + BRD  
**Narrows to:** product capabilities, user outcomes, and priorities

## Purpose

Define what the product will do to achieve business objectives. Feature-level thinking starts here, not before.

## Required sections

| Section | Content |
|---------|---------|
| **Product overview** | One-paragraph product description tied to vision |
| **Goals** | Product goals mapped to BRD objectives |
| **User personas** | Primary personas with goals, pain points, context |
| **User stories / outcomes** | Outcome-oriented capabilities (not implementation) |
| **Feature priorities** | MoSCoW or P0/P1/P2 with rationale |
| **Out of scope** | Product-level exclusions (inherits exec non-goals) |
| **Release phasing** | MVP vs v1 vs future (if applicable) |

## Extraction method (discovery)

1. For each BRD objective, ask "what product capability delivers this?"
2. Write user stories as outcomes: "As [persona], I can [outcome] so that [business value]."
3. Challenge feature requests against exec-summary non-goals.
4. Prioritize ruthlessly — force rank if user lists >5 features.
5. Separate MVP from v1 explicitly.

## Traceability

- Assign ids: `prd-goal-N`, `prd-story-N`, `prd-feature-N`.
- Each goal traces to `brd-obj-N`.
- Each story traces to `prd-goal-N` and a persona.
- Each feature traces to at least one story.

## Done-when checklist

- [ ] Product overview links to exec-summary vision
- [ ] Every BRD objective has at least one product goal
- [ ] Personas defined with goals and pain points
- [ ] User stories are outcome-oriented (no implementation detail)
- [ ] Features prioritized with explicit MVP boundary
- [ ] Out-of-scope items documented
- [ ] No feature contradicts exec-summary non-goals or BRD business rules
