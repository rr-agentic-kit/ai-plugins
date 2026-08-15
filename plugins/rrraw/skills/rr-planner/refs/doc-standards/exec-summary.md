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
| **Posture** | Existence × commitment for this session (`greenfield`/`existing` × `unsigned`/`signed_v1`) | Unranked leaf (`MoSCoW: —`) |
| **Vision** | One-paragraph aspirational end state (what success looks like) | Unranked leaf (`MoSCoW: —`) |
| **Problem** | Specific pain being solved; who feels it; cost of inaction | Unranked leaf |
| **Why now** | Timing drivers — market shift, regulation, tech enabler, competitive pressure | Ranked leaves |
| **Success metrics** | 2–5 measurable outcomes tied to vision (not features) | Ranked leaves |
| **Constraints** | Hard boundaries — budget, timeline, regulatory, technical | Ranked leaves |
| **Non-goals** | Explicit exclusions to prevent scope creep | Ranked leaves; `Won't` by definition |

IDs, parent walk, split, spec/build: [item-schema.md](item-schema.md). Prefix `ES`. Posture, vision, and problem are the unranked anchors. Metrics, constraints, non-goals, and why-now use Must/Should/Could/Won’t. Posture classification: [project-posture.md](../project-posture.md).

## Extraction method (discovery)

1. If `session_state.project_posture` is missing or unconfirmed, run the posture gate first ([project-posture.md](../project-posture.md)) — scan, confirm, persist the Posture leaf. Do not start vision while posture is unset.
2. Start with user's free-form description; extract vision and problem separately.
3. If user leads with solution → redirect: "What problem does [solution] solve?"
4. Probe for "why now" if not stated.
5. Push back on unmeasurable success metrics → ask for quantifiable proxies.
6. Record constraints and non-goals as first-class items, not footnotes. Under `existing`, shipped behavior lands here (and non-goals), not as PRD features.
7. Mint `ES-n` ids; default `spec: idea`; promote to `draft` while specifying. Do not auto-promote to `ready`.
8. Feature-level volunteer during this level → [note-sessions.md](../note-sessions.md), not an ES fact.

## Traceability

- Immediate `parent:` is `—` for roots; nested children point at `ES-n`.
- Downstream items point at an `ES-*` id (usually a metric or the vision/problem leaf).
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

- [ ] Posture leaf present; matches confirmed `session_state.project_posture`
- [ ] Vision is outcome-focused (not feature list)
- [ ] Problem names affected users/personas
- [ ] At least one "why now" driver documented
- [ ] Success metrics are measurable or have defined measurement proxy
- [ ] At least one constraint and one non-goal stated
- [ ] Items use `ES-{n}` / `ES-{n.m}` per item-schema; leaves have `MoSCoW` (or `—` on posture/vision/problem)
- [ ] Zero unresolved ambiguities at this level
- [ ] User confirmed accuracy via goal-anchor
