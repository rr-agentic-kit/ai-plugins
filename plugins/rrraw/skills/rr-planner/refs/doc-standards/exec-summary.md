# exec-summary

**Cascade level:** 1 (foundation)  
**Inherits from:** user input, conversation context  
**Narrows to:** strategic vision, problem framing, and session posture for MRD  
**Priority method:** MoSCoW — [item-schema.md](item-schema.md)  
**Blind-spots (stage-exit):** Scan only the exec-summary row in [blind-spots.md](../blind-spots.md) (`in_scope` + `inherit_check`). Do not copy the taxonomy here.

## Purpose

Anchor all downstream docs to a clear vision, problem statement, and rationale. Every later requirement must trace back here.

## Required sections

| Section | Content | Items |
|---------|---------|-------|
| **Posture** | Existence × commitment for this session (`greenfield`/`existing` × `unsigned`/`signed_v1`) plus `domain_context` | Unranked leaf (`_moscow_: —`) |
| **Vision** | One-paragraph aspirational end state (what success looks like) | Unranked leaf (`_moscow_: —`) |
| **Problem** | Specific pain being solved; who feels it; cost of inaction | Unranked leaf |
| **What must be true** | Smallest set of premises the cascade stands on; claim-class + evidence bar per premise | Unranked leaf (`_moscow_: —`) |
| **Viability verdict** | Panel verdict `proceed` … `kill` with dissent named; binding | Unranked leaf (`_moscow_: —`) |
| **Why now** | Timing drivers — market shift, regulation, tech enabler, competitive pressure | Ranked leaves |
| **Success metrics** | 2–5 measurable outcomes tied to vision (not features) | Ranked leaves |
| **Constraints** | Hard boundaries — budget, timeline, regulatory, technical | Ranked leaves |
| **Non-goals** | Explicit exclusions to prevent scope creep | Ranked leaves; `Won't` by definition |

Prefix `ES`. Posture, vision, problem, what-must-be-true, and viability verdict are the unranked anchors. Metrics, constraints, non-goals, and why-now use Must/Should/Could/Won’t. Posture classification: [project-posture.md](../project-posture.md). Premise test and verdict: [expert-panel.md](../expert-panel.md). Ranked leaves carry `Rationale`.

## Extraction method (discovery)

1. If `session_state.project_posture` is missing or unconfirmed, run the posture gate first ([project-posture.md](../project-posture.md)) — scan, confirm (including `domain_context`), persist the Posture leaf. Do not start vision while posture is unset.
2. Start with user's free-form description; extract vision and problem separately.
3. If user leads with solution → redirect: "What problem does [solution] solve?"
4. Run the **premise test** ([expert-panel.md](../expert-panel.md)): sit founder/CEO, seed investor, domain practitioner; write What-must-be-true; classify claims; evidence loop; write Viability verdict. Binding.
5. Probe for "why now" if not stated.
6. Push back on unmeasurable success metrics → ask for quantifiable proxies.
7. Record constraints and non-goals as first-class items, not footnotes. Under `existing`, shipped behavior lands here (and non-goals), not as PRD features.
8. Mint `ES-n` ids; default `spec: idea`; promote to `draft` while specifying. Do not auto-promote to `ready`. Mint ledger rationales for ranked leaves before compose.
9. Feature-level volunteer during this level → [note-sessions.md](../note-sessions.md), not an ES fact.

## Traceability

- Immediate `parent:` is `—` for roots; nested children point at `ES-n`.
- Downstream items point at an `ES-*` id (usually a metric or the vision/problem leaf).
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

- [ ] Posture leaf present; matches confirmed `session_state.project_posture` including `domain_context`
- [ ] Vision is outcome-focused (not feature list)
- [ ] Problem names affected users/personas
- [ ] What-must-be-true names premises with claim class and evidence bar
- [ ] Viability verdict recorded; binding `hold`/`kill` unresolved → do not freeze
- [ ] At least one "why now" driver documented
- [ ] Success metrics are measurable or have defined measurement proxy
- [ ] At least one constraint and one non-goal stated
- [ ] Items use `ES-{n}` / `ES-{n.m}` per item-schema; leaves have `_moscow_` (or `—` on unranked anchors); ranked leaves have `_rationale_`
- [ ] Zero unresolved ambiguities at this level
- [ ] User confirmed accuracy via goal-anchor **or** evidence bar met / risk recorded
