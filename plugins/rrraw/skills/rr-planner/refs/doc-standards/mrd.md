# mrd (Market Requirements Document)

**Cascade level:** 2  
**Inherits from:** exec-summary (vision, problem, constraints)  
**Narrows to:** market context relevant to the stated vision

## Purpose

Ground the initiative in market reality — segments, competitors, trends — without becoming a full market research report.

## Required sections

| Section | Content |
|---------|---------|
| **Market overview** | Segment definition aligned to exec-summary problem |
| **Target segments** | Primary and secondary segments with sizing estimates or proxies |
| **Competitive landscape** | Key players, positioning, differentiation gaps |
| **Market trends** | 2–4 trends that support "why now" |
| **Customer needs** | Unmet needs mapped to exec-summary problem |
| **Market risks** | External threats — regulation, commoditization, disruption |

## Extraction method (discovery)

1. Inherit vision/problem; ask "who buys vs who uses?"
2. For competitors: accept user-stated list; probe for indirect alternatives.
3. Defer broad market sizing to research phase — record as assumption if unknown.
4. Map each customer need to `exec-problem` or `exec-vision`.
5. Flag claims needing validation → `research_deferred[]`.

## Traceability

- Assign ids: `mrd-segment-N`, `mrd-competitor-N`, `mrd-need-N`, `mrd-risk-N`.
- Each segment must trace to `exec-problem` or `exec-vision`.
- Each need must trace to at least one exec-level id.

## Done-when checklist

- [ ] Primary target segment defined with boundaries
- [ ] At least 2 competitors or alternatives named
- [ ] Market trends linked to exec-summary "why now"
- [ ] Customer needs map to exec-summary problem
- [ ] Market risks identified (at least one)
- [ ] Unvalidated claims marked as assumptions
- [ ] No contradiction with exec-summary constraints/non-goals
