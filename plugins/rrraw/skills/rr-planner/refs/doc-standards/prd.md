# prd (Product Requirements Document)

**Cascade level:** Plan primary doc  
**Inherits from:** Frozen executive-summary + MRD + BRD + `business-case.yaml`  
**Narrows to:** Full feature requirement sets, scored backlog, WWAS AC, selection status  
**Priority method:** RICE on features; RIC on stories; `primary`/`support` on goals; **P1/P2/P3 on requirement leaves** — `refs/planning/doc-standards/item-schema.md`  
**Panel seats:** Founder dual-lens (product + system) — `skills/rr-planner/refs/plan-interview.md`  
**Blind-spots (stage-exit):** Scan Plan technical-plan row in `skills/rr-planner/refs/blind-spots.md`. Do not copy the taxonomy here.

## Purpose

Define **what** the product will do: full requirement honesty + thin build selection. PRD is standing feature truth — not a cut-pass, not a sprint plan, not a release/version plan (future: release groups frozen slices into versions).

## PRD-shape reflection

Before minting structure, recommend `prd_shape` + `scope_mode` (+ optional `arch_doc_mode`, interview mode). User confirms; persist in `session_state.project_posture` and the **Shape** section (`skills/rr-planner/refs/project-posture.md`).

| Factor | Tips `story_led` / `discovery` | Tips `feature_led` / `closed` |
|--------|-------------------------------|------------------------------|
| **Scope certainty** | Unknown market-minimum; exploring fit | Known MVP contract; packaging capabilities |
| Primary audience of the doc | Outcome alignment (founder dual-lens) | Spec for delivery / capability buyers |
| Market shape | B2C, persona-heavy | B2B, buyer≠user |
| What gets prioritized | Outcomes / JTBD first | Capabilities / RICE-on-features first |
| WIP style | Stories before capabilities named | Features first; stories as usage angles |
| Downstream need | Slice kernel later | Needs architecture spine sooner |
| NFR criticality | Few product-level NFRs | Several NFRs are product commitments on PRD |

**Output:** `prd_shape: story_led | feature_led | hybrid` + `scope_mode: discovery | closed`. Revisit only on explicit user change or objective shift.

## Required sections

| Section | Content | Items |
|---------|---------|-------|
| **Shape** | Confirmed `prd_shape` + `scope_mode` (+ arch/interview mode if set) | Prose (unnumbered) |
| **Product overview** | One-paragraph product description tied to vision | Prose (unnumbered) |
| **Goals** | Product goals mapped to BRD objectives | Ranked leaves; `_goal-type_: primary \| support` |
| **User personas** | Primary personas with goals, pain points, context | Prose (unnumbered); meaningful default for B2C, optional for B2B |
| **User stories / outcomes** | Outcome-oriented capabilities (not implementation) | Ranked leaves; RIC scoring; optional job-story body |
| **Features** | Capabilities that deliver stories | Ranked leaves; full RICE; Effort same-sitting with architecture |
| **Requirements** | Full set per feature — never shrunk for “build now” | Ranked leaves; `_priority_: P1\|P2\|P3`; `_status_:` selection |
| **Acceptance (WWAS)** | Why / What / observable Acceptance — product pass/fail | Prose or leaves tied to selected requirements; smell-gate before slice freeze |
| **Out of scope** | Product-level exclusions (inherits exec non-goals) | Ranked leaves; no RICE |

Prefix `PRD`. Product scoping + observable AC. **P-tags only on requirement leaves.** No MoSCoW. No sprint / capacity / velocity ceremony. No release-phasing doc in this pass. Personas stay a section; stories name a persona in the body — they do not parent to a persona id.

Selection: `_status_: deferred | selected | in_progress | delivered` on leaves. Selecting “build now” **never** deletes/shrinks the full set and never invents a second scope doc. Language: **slice / phase**.

## RICE scoring

Persist **factors only** — composed `(R×I×C)/E` score is **not stored**.

| Factor | Features | Stories | Values |
|--------|----------|---------|--------|
| **Reach** | ✓ | ✓ | 10–100% of a **named** target — state the denominator |
| **Impact** | ✓ | ✓ | `0.25` Minimal · `0.5` Low · `1` Medium · `2` High · `3` Massive |
| **Confidence** | ✓ | ✓ | `low`→0.5 · `medium`→0.8 · `high`→1.0 |
| **Effort** | ✓ | — | Fibonacci `1, 2, 3, 5, 8, 13` on **features only** — **refuse** without same-sitting architecture (spine and/or feature delta) |

Stories score **RIC** (no Effort). Features score full **RICE**. Goals use `primary`/`support` only. Requirement leaves use P1–P3. Out-of-scope items get no RICE factors. Framework choice: `skills/rr-planner/refs/prioritization-lens.md`.

### Story↔feature alignment

After scoring, validate RICE/RIC consistency and adherence to parent feature intent.

## NFR + mechanism placement

| Kind | Where |
|------|-------|
| Product-facing NFR / WWAS AC | PRD |
| Standing invariants | `architecture.md` (+ constitution) |
| Feature mechanism | `deltas/<feature-id>.md` |
| Discover early parking only | Root `tech.md` — **Plan does not author AC/ADR there** |

## Extraction method (Plan interview)

Follow `skills/rr-planner/refs/plan-interview.md`: objective → capability → story → feature → full requirements → select → AC smell → slice freeze.

1. PRD-shape (+ arch mode) if not confirmed.
2. For each BRD objective: “what product capability delivers this?”
3. Stories as outcomes (or job stories when appropriate).
4. Challenge feature requests against executive-summary non-goals. Under `existing`, shipped behavior is a constraint — do not restate as a feature to build.
5. Score with architecture in the same pass. Incomplete RICE ok on `idea`/`draft` in `discovery` mode.
6. Capture full requirement set with P1–P3; select via status.
7. WWAS + `skills/rr-planner/refs/req-smell.md` before slice freeze.
8. Slice freeze → `skills/rr-planner/refs/execute-handoff.md`.

## Traceability (C2-7)

- Cross-doc `parent:` is **≥1 `ES-*` id OR ≥1 `BRD-*` id** (OR, not AND).
- Same-doc nest: `PRD-n` → `PRD-n.m`.
- Each goal walks to a BRD objective. Each story walks to a goal (and names a persona in the body).
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

- [ ] Shape section records confirmed `prd_shape` + `scope_mode`
- [ ] Product overview links to executive-summary vision
- [ ] Every BRD objective has at least one product goal
- [ ] User stories are outcome-oriented (fail: implementation detail)
- [ ] Features have RICE factors (or explicit `—` while `idea`/`draft`) with Effort only after architecture pass
- [ ] Requirement leaves have P1–P3; selection via `_status_` without shrinking the set
- [ ] WWAS AC smell-clean (or holds) before slice freeze
- [ ] Every PRD item has cross-doc parent ≥1 ES **or** ≥1 BRD
