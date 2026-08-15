# exec-summary

**Cascade level:** 1 (foundation)  
**Inherits from:** user input, conversation context  
**Narrows to:** strategic vision and problem framing for MRD  
**Priority method:** MoSCoW — [item-schema.md](item-schema.md)  
**Blind-spots (stage-exit):** Scan only the exec-summary row in [blind-spots.md](../blind-spots.md) (`in_scope` + `inherit_check`). Do not copy the taxonomy here.

## Purpose

Anchor all downstream docs to a clear vision, problem statement, and rationale. Every later requirement must trace back here.

## Required sections

| Section | Content | Items |
|---------|---------|-------|
| **Vision** | One-paragraph aspirational end state (what success looks like) | Unranked leaf (`MoSCoW: —`) |
| **Problem** | Specific pain being solved; who feels it; cost of inaction | Unranked leaf |
| **Why now** | Timing drivers — market shift, regulation, tech enabler, competitive pressure | Ranked leaves |
| **Success metrics** | 2–5 measurable outcomes tied to vision (not features) | Ranked leaves |
| **Constraints** | Hard boundaries — budget, timeline, regulatory, technical | Ranked leaves |
| **Non-goals** | Explicit exclusions to prevent scope creep | Ranked leaves; `Won't` by definition |

IDs, parent walk, split, spec/build: [item-schema.md](item-schema.md). Prefix `ES`. Vision and problem are the unranked anchors. Metrics, constraints, non-goals, and why-now use Must/Should/Could/Won’t.

## Extraction method (discovery)

1. Start with user's free-form description; extract vision and problem separately.
2. If user leads with solution → redirect: "What problem does [solution] solve?"
3. Probe for "why now" if not stated.
4. Push back on unmeasurable success metrics → ask for quantifiable proxies.
5. Record constraints and non-goals as first-class items, not footnotes.
6. Mint `ES-n` ids; default `spec: idea`; promote to `draft` while specifying. Do not auto-promote to `ready`.

## Traceability

- Immediate `parent:` is `—` for roots; nested children point at `ES-n`.
- Downstream items point at an `ES-*` id (usually a metric or the vision/problem leaf).
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

- [ ] Vision is outcome-focused (not feature list)
- [ ] Problem names affected users/personas
- [ ] At least one "why now" driver documented
- [ ] Success metrics are measurable or have defined measurement proxy
- [ ] At least one constraint and one non-goal stated
- [ ] Items use `ES-{n}` / `ES-{n.m}` per item-schema; leaves have `MoSCoW` (or `—` on vision/problem)
- [ ] Zero unresolved ambiguities at this level
- [ ] User confirmed accuracy via goal-anchor
