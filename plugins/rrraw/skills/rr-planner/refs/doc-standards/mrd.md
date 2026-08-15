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
| **Target segments** | Primary and secondary segments with sizing estimates or proxies | Unranked leaves (`Kano: —`); primary/secondary in body |
| **Competitive landscape** | Key players, positioning, differentiation gaps | Unranked leaves |
| **Market trends** | 2–4 trends that support "why now" | Unranked leaves |
| **Customer needs** | Unmet needs mapped to exec-summary problem | Ranked leaves: `basic` / `performance` / `delighter` |
| **Market risks** | External threats — regulation, commoditization, disruption | Unranked leaves; impact × likelihood in body |

IDs, parent walk, split, spec/build: [item-schema.md](item-schema.md). Prefix `MRD`. Kano is the native model for this layer — do not flatten needs into MoSCoW.

## Extraction method (discovery)

1. Inherit vision/problem; ask "who buys vs who uses?"
2. For competitors: accept user-stated list; probe for indirect alternatives.
3. Defer broad market sizing to research phase — record as assumption if unknown.
4. Map each customer need to an `ES-*` parent (problem or vision).
5. Classify needs as Kano `basic` / `performance` / `delighter` — do not use Must/Should/Could.
6. Flag claims needing validation → `research_deferred[]`.

## Traceability

- Cross-doc `parent:` is an `ES-*` id. Same-doc nest: `MRD-n` → `MRD-n.m`.
- Each segment and need walks to exec-summary (problem or vision).
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

- [ ] Primary target segment defined with boundaries
- [ ] At least 2 competitors or alternatives named
- [ ] Market trends linked to exec-summary "why now"
- [ ] Customer needs map to exec-summary problem and have Kano class
- [ ] Market risks identified (at least one) with impact × likelihood
- [ ] Unvalidated claims marked as assumptions
- [ ] Items use `MRD-{n}` / `MRD-{n.m}` per item-schema
- [ ] No contradiction with exec-summary constraints/non-goals
