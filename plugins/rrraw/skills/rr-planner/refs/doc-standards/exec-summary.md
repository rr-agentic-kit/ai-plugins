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
| **Posture** | Existence × commitment for this session (`greenfield`/`existing` × `unsigned`/`signed_v1`) plus `domain_context` | Prose (unnumbered) |
| **Vision** | One-paragraph aspirational end state (what success looks like) | Prose (unnumbered) |
| **Problem** | Specific pain being solved; who feels it; cost of inaction | Prose (unnumbered) |
| **What must be true** | Smallest set of premises the cascade stands on; claim-class + evidence bar per premise | Prose (unnumbered) |
| **Viability verdict** | Panel verdict `proceed` … `kill` with dissent named; binding | Prose (unnumbered) |
| **Why now** | Timing drivers — market shift, regulation, tech enabler, competitive pressure | Ranked leaves |
| **Success metrics** | 2–5 measurable outcomes tied to vision (not features) | Ranked leaves |
| **Constraints** | Hard boundaries — budget, timeline, regulatory, technical | Ranked leaves |
| **Non-goals** | Explicit exclusions to prevent scope creep | Ranked leaves; `Won't` by definition |

Prefix `ES`. Mint `ES-n` only for ranked sections (why now, metrics, constraints, non-goals). Posture, vision, problem, what-must-be-true, and viability verdict stay prose. Metrics, constraints, non-goals, and why-now use Must/Should/Could/Won’t. Posture classification: [project-posture.md](../project-posture.md). Premise test and verdict: [expert-panel.md](../expert-panel.md). Ranked leaves carry `Rationale`.

## Extraction method (discovery)

1. If `session_state.project_posture` is missing or unconfirmed, run the posture gate first ([project-posture.md](../project-posture.md)) — scan, confirm (including `domain_context`), persist the Posture **section**. Do not start vision while posture is unset.
2. Start with user's free-form description; extract vision and problem separately.
3. If user leads with solution → redirect: "What problem does [solution] solve?"
4. Run the **premise test** ([expert-panel.md](../expert-panel.md)): sit founder/CEO, seed investor, domain practitioner; write What-must-be-true; classify claims; evidence loop; write Viability verdict. Binding. Both are prose sections, not `ES-*` ids.
5. Probe for "why now" if not stated.
6. Push back on unmeasurable success metrics → ask for quantifiable proxies.
7. Record constraints and non-goals as first-class items, not footnotes. Under `existing`, shipped behavior lands here (and non-goals), not as PRD features.
8. Mint `ES-n` ids for ranked sections only; default `spec: idea`; promote to `draft` while specifying. Do not auto-promote to `ready`. Mint ledger rationales for ranked leaves before compose.
9. Feature-level volunteer during this level → [note-sessions.md](../note-sessions.md), not an ES fact.

## Traceability

- Immediate `parent:` is `—` for roots; nested children point at `ES-n`.
- Downstream items point at a ranked `ES-*` id (usually a metric). `goal_ref` cites a ranked `ES-*` only.
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

Per-doc bars only. Gate 1, the script, shared success-criteria, Gate 2 / Gate 7, and Gate 6 `in_scope` own the rest.

- [ ] Posture matches confirmed `session_state.project_posture` including `domain_context`
- [ ] Vision is outcome-focused (fail: a feature list)
- [ ] What-must-be-true names premises with claim class and evidence bar (fail: a bare slogan)
- [ ] Success metrics are measurable or have a defined measurement proxy (fail: "fast")
- [ ] At least one constraint **and** one non-goal stated
