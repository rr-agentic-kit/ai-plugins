# mrd (Market Requirements Document)

**Cascade level:** 2  
**Inherits from:** exec-summary (vision, problem, constraints)  
**Narrows to:** market context relevant to the stated vision  
**Priority method:** Kano on needs — [item-schema.md](item-schema.md)  
**Blind-spots (stage-exit):** Scan only the mrd row in [blind-spots.md](../blind-spots.md) (`in_scope` + `inherit_check`). Do not copy the taxonomy here.

## Purpose

Ground the initiative in market reality — segments, competitors, trends — without becoming a full market research report.

## Required sections

| Section | Content | Items |
|---------|---------|-------|
| **Market overview** | Segment definition aligned to exec-summary problem | Prose (unnumbered) |
| **TAM / SAM / SOM** | Evidence-backed sizing. `market_type: external`: TAM, SAM, SOM with sources. `market_type: internal`: affected-teams × hours × loaded cost — **no TAM**. Mandatory incumbent **and** do-nothing comparison in either variant | Unranked leaves (`_kano_: —`); numbers cite ledger `evidence` ids |
| **Target segments** | Primary and secondary segments with sizing estimates or proxies | Unranked leaves (`_kano_: —`); primary/secondary in body |
| **Competitive landscape** | Key players, positioning, differentiation gaps; incumbent named | Unranked leaves |
| **Market trends** | 2–4 trends that support "why now" | Unranked leaves |
| **Customer needs** | Unmet needs mapped to exec-summary problem | Ranked leaves: `basic` / `performance` / `delighter` |
| **Market risks** | External threats — regulation, commoditization, disruption | Unranked leaves; impact × likelihood in body |

Prefix `MRD`. Kano is the native model for this layer — do not flatten needs into MoSCoW. Sizing is a required evidence-backed section, not a research-phase deferral (`market_type: internal` skips TAM). Ranked leaves carry `Rationale`. Binding Gate 7 at this level ([expert-panel.md](../expert-panel.md)).

## Extraction method (discovery)

1. Inherit vision/problem; ask "who buys vs who uses?"
2. For competitors: accept user-stated list; probe for indirect alternatives. **Name an incumbent** (or the internal status quo) and a do-nothing option.
3. Size the market **in this level**, evidence-backed. External: TAM/SAM/SOM with ledger evidence. Internal: teams × hours × loaded cost; skip TAM. Do not invent a number to fill the section — `hold` or `vague` is legal; a fabricated TAM is not.
4. Map each customer need to an `ES-*` parent (problem or vision).
5. Classify needs as Kano `basic` / `performance` / `delighter` — do not use Must/Should/Could. Mint rationales for ranked needs.
6. Flag residual gaps beyond the claim-class budget → `research_deferred[]` with a named evidence bar, or Gate 7 `hold`.

## Traceability

- Cross-doc `parent:` is an `ES-*` id. Same-doc nest: `MRD-n` → `MRD-n.m`.
- Each segment and need walks to exec-summary (problem or vision).
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

- [ ] Primary target segment defined with boundaries
- [ ] TAM/SAM/SOM (external) or teams×hours×cost (internal) present with evidence ids or an explicit `hold`
- [ ] Incumbent **and** do-nothing compared
- [ ] At least 2 competitors or alternatives named
- [ ] Market trends linked to exec-summary "why now"
- [ ] Customer needs map to exec-summary problem and have Kano class + `_rationale_`
- [ ] Market risks identified (at least one) with impact × likelihood
- [ ] Unvalidated claims marked as assumptions or ledger evidence `unknown`
- [ ] Items use `MRD-{n}` / `MRD-{n.m}` per item-schema
- [ ] No contradiction with exec-summary constraints/non-goals
- [ ] Binding viability verdict recorded
