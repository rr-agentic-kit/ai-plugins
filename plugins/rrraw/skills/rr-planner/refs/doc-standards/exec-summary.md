# exec-summary

**Cascade level:** 1 (foundation)  
**Inherits from:** user input, conversation context  
**Narrows to:** strategic vision and problem framing for MRD

## Purpose

Anchor all downstream docs to a clear vision, problem statement, and rationale. Every later requirement must trace back here.

## Required sections

| Section | Content |
|---------|---------|
| **Vision** | One-paragraph aspirational end state (what success looks like) |
| **Problem** | Specific pain being solved; who feels it; cost of inaction |
| **Why now** | Timing drivers — market shift, regulation, tech enabler, competitive pressure |
| **Success metrics** | 2–5 measurable outcomes tied to vision (not features) |
| **Constraints** | Hard boundaries — budget, timeline, regulatory, technical |
| **Non-goals** | Explicit exclusions to prevent scope creep |

## Extraction method (discovery)

1. Start with user's free-form description; extract vision and problem separately.
2. If user leads with solution → redirect: "What problem does [solution] solve?"
3. Probe for "why now" if not stated.
4. Push back on unmeasurable success metrics → ask for quantifiable proxies.
5. Record constraints and non-goals as first-class facts, not footnotes.

## Traceability

- Assign ids: `exec-vision`, `exec-problem`, `exec-metric-N`, `exec-constraint-N`, `exec-nongoal-N`.
- All downstream objectives must reference at least one exec-level id.

## Done-when checklist

- [ ] Vision is outcome-focused (not feature list)
- [ ] Problem names affected users/personas
- [ ] At least one "why now" driver documented
- [ ] Success metrics are measurable or have defined measurement proxy
- [ ] At least one constraint and one non-goal stated
- [ ] Zero unresolved ambiguities at this level
- [ ] User confirmed accuracy via goal-anchor
