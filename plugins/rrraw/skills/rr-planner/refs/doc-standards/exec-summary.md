# exec-summary

**Cascade level:** 1 (foundation)  
**Inherits from:** user input, conversation context  
**Narrows to:** strategic vision, problem framing, and session posture for MRD  
**Priority method:** MoSCoW on **Functional deliverables only** — [item-schema.md](item-schema.md)  
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
| **Why now** | Timing drivers — market shift, regulation, tech enabler, competitive pressure | Ranked leaves (no MoSCoW) |
| **Success metrics** | 2–5 measurable **outcomes** tied to vision (not features, not feature SLAs) | Ranked leaves (no MoSCoW) |
| **Functional deliverables** | Product-success capabilities the initiative must ship — Must-only in practice | Ranked leaves; MoSCoW (Must in practice) |
| **Constraints** | Hard boundaries — budget, timeline, regulatory, quality, technical; NFR outcomes as tagged constraints | Ranked leaves (no MoSCoW); optional `_tag_:` |
| **Non-goals** | Explicit exclusions to prevent scope creep | Ranked leaves (no MoSCoW) |
| **Horizons** *(optional)* | Thematic future buckets (≤5); not an exhaustive feature list | Ranked leaves (no MoSCoW); may point at `later.md` |

Prefix `ES`. Mint `ES-n` only for ranked sections. Posture, vision, problem, what-must-be-true, and viability verdict stay prose. Ranked leaves carry `Rationale`. Posture classification: [project-posture.md](../project-posture.md). Premise test and verdict: [expert-panel.md](../expert-panel.md).

### Section scope (agent-facing)

| Section | In scope | Does not belong |
|---------|----------|-----------------|
| **Why now** | Timing drivers, window-of-opportunity, competitive/regulatory pressure | Feature lists, implementation choices, channel tactics |
| **Success metrics** | Outcome/result measures (adoption %, revenue, retention, task completion) | Feature SLAs (p95 latency → Constraint `quality`); decorative metrics without teeth |
| **Functional deliverables** | Named product capabilities required for success (e.g. anonymous browse, multi-language support) | Policy mechanisms (→ Constraints); channel tactics (→ PRD); implementation detail (→ `tech.md`) |
| **Constraints** | Hard limits stated as outcomes (`Must comply with GDPR`, `≤$50k budget`, `p95 < 200ms`) with optional `_tag_:` (`capacity`, `regulatory`, `quality`, `technical`, …) | Feature descriptions; lawful-path channel picks; consent UI flows |
| **Non-goals** | Explicit exclusions for this initiative | Deferred work (→ `later.md` or Horizons) |
| **Horizons** | Thematic future direction (≤5 items); may reference `later.md` | Exhaustive backlog; RICE-ranked features (→ PRD) |

## Metric teeth (T1r-6, T1r-7)

An empty or decorative metric is **worse than none**. Flag to complete, or move to `later.md`/notes if the user agrees.

A **proxy** is allowed only when:
1. A **deadline** to define/instrument the real measure is stated, **or**
2. The proxy is **anchored** to a currently measurable metric it is expected to move.

Success metrics touching **mode-gated** features must state the measurable population explicitly (e.g. "80% of logged-in users complete onboarding within 7 days" — not "80% of users" when the feature requires login).

## Consent derivation (T7-4)

Consent scope is **derived, not a fixed list**. Any Functional-deliverable Must implying personal-data collection for behavior or analysis **auto-pairs** a `regulatory`-tagged consent constraint, emitted proactively — not user-prompted per item. The constraint states the **outcome** ("consent required for taste profile + feedback; see/delete/change"); mechanism routes to `tech.md`.

## Domain-routing triggers

When GDPR, i18n, distribution, security, or enrichment-law topics surface during ES discovery, load [domain-routing.md](../domain-routing.md) and emit a placement table **once per distinct domain topic** — user reviews once, skill applies routing silently thereafter. Examples:

- **GDPR/privacy** — regime + consent outcome at ES (Constraints); business rules at BRD; product backlog at PRD; mechanism at `tech.md`
- **i18n** — "multi-language support" is a Functional deliverable Must; locale matrix and copy workflow are PRD
- **Distribution** — strategy ("market-compatible channels") at ES when success-critical; beta/alpha/private-link tactics at PRD only ([domain-routing.md](../domain-routing.md) § distribution)

## Extraction method (discovery)

1. If `session_state.project_posture` is missing or unconfirmed, run the posture gate first ([project-posture.md](../project-posture.md)) — scan, confirm (including `domain_context`), persist the Posture **section**. Do not start vision while posture is unset.
2. Start with user's free-form description; extract vision and problem separately.
3. If user leads with solution → redirect: "What problem does [solution] solve?"
4. Run the **premise test** ([expert-panel.md](../expert-panel.md)): sit founder/CEO, seed investor, domain practitioner; write What-must-be-true; classify claims; evidence loop; write Viability verdict. Binding. Both are prose sections, not `ES-*` ids.
5. Probe for "why now" if not stated.
6. Separate **outcomes** (Success metrics) from **capabilities** (Functional deliverables) from **limits** (Constraints). Misfiled features (e.g. "must be in English" as a constraint) → refile to Functional deliverables.
7. Push back on unmeasurable success metrics → apply metric-teeth rule; offer proxy with deadline or anchor.
8. Record constraints (with `_tag_:` when helpful) and non-goals as first-class items. Under `existing`, shipped behavior lands in Constraints / non-goals, not as PRD features.
9. Mint `ES-n` ids for ranked sections only; default `spec: idea`; promote to `draft` while specifying. Do not auto-promote to `ready`. Mint ledger rationales for ranked leaves before compose.
10. Feature-level detail volunteered during this level → [note-sessions.md](../note-sessions.md), not an ES fact.
11. Mode existence (e.g. anonymous browse) can be its own Functional-deliverable Must when success-critical — separate from the privacy/consent constraint (T7-1).

## Traceability

- Immediate `parent:` is `—` for roots; nested children point at `ES-n`.
- Downstream items point at a ranked `ES-*` id (usually a metric or functional deliverable). `goal_ref` cites a ranked `ES-*` only.
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

Per-doc bars only. Gate 1, the script, shared success-criteria, Gate 2 / Gate 7, and Gate 6 `in_scope` own the rest.

- [ ] Posture matches confirmed `session_state.project_posture` including `domain_context`
- [ ] Vision is outcome-focused (fail: a feature list)
- [ ] What-must-be-true names premises with claim class and evidence bar (fail: a bare slogan)
- [ ] Success metrics are measurable outcomes with teeth (fail: "fast", "good UX", feature SLAs)
- [ ] Functional deliverables are Must-only capabilities (fail: policy mechanisms or channel tactics)
- [ ] At least one constraint **and** one non-goal stated
- [ ] Personal-data Musts have paired consent constraints
