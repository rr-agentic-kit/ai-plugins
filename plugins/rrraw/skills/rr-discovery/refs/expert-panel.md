# expert-panel

**Owner:** Seat roster, conduct protocol, evidence loop, and viability verdict. The panel co-designs — a seat that blocks owes an alternative.

**Load when:** Exec-summary premise test; every level's Gate 7; evidence round after a premise-critical claim; `--resume` when `viability[]` or the re-decision queue is open. Not during compose (compose consumes minted rationale ids; it does not sit the panel).

The verdict is a **state**, not an exit. Invalidation never auto-flips item status ([decision-ledger.md](../../../refs/planning/decision-ledger.md)).

## domain_context

Instantiate seats from `session_state.project_posture.domain_context` — capture schema: [project-posture.md](project-posture.md). Do not seat a generic "CFO". Missing after confirm → blocking clarification. Do not invent an industry.

`market_type: internal` is a **required variant**, not a nicety. Internal platform work has no TAM. The MRD sizing gate swaps sizing for affected-teams × hours × loaded cost, build-vs-buy, and do-nothing. Without the variant the gate produces garbage verdicts on internal work.

## Roster (role × level)

Every level seats the **domain practitioner** who lives the problem, instantiated from `domain_context` ("a CFO at a mid-market 3PL", not "a CFO"). Plus the role seats below.

| Level | Role seats | Binding |
|-------|------------|---------|
| executive-summary | Founder/CEO + seed investor + domain practitioner | Binding |
| mrd | CMO + growth investor + domain practitioner | Binding |
| brd | CFO + COO + domain practitioner | Advisory |
| prd | Head of product + UX + domain practitioner | Advisory |

Binding: a `hold` / `kill` / `pivot` blocks freeze and advance. Advisory: record the verdict and dissent; user may accept and proceed (still write the ledger). Dissent between seats is recorded, **never averaged** — the disagreement is the signal.

Do not drop a seat because the user is solo. Argue both sides; the empty chair is the point.

## Conduct protocol (every turn)

A turn that only critiques is incomplete. When blocking, the seat owes a path.

1. **Name the standard** being applied (investor hurdle, operational constraint, practitioner lived-experience, SRE error budget).
2. **Ask** the question that standard requires.
3. **State the evidence bar** — what would satisfy it. Prefer a measurable bar; an honest qualitative bar beats a fabricated number ([decision-ledger.md](../../../refs/planning/decision-ledger.md) no-fabricated-numbers). For legal/regulatory claims, prefer **real enforcement-in-practice and case statistics** over literal statute reading (T6-1).
4. **If blocking: owe an alternative.** Put 2–3 options on the comparison table in [blind-spots.md](blind-spots.md), including do-nothing / buy / pivot-the-premise. Critique without a proposed path is an incomplete turn. The option-generation prompt ("Name two paths that still move an ES metric if this premise is wrong") is the **sole `hold` trigger** — a T6-1 legal-risk tier is not itself a block.

Record the turn in raw-history with `source: panel` ([output-formats.md](../../../refs/planning/output-formats.md)). Mint the rationale in the ledger at the moment the decision is made — before compose references the id.

## Claim classes and evidence loop

Discovery search is budgeted by **claim class**, not a flat cap of 2. Research phase ([research-method.md](research-method.md)) stays the broad post-composition pass.

| Class | What | Budget |
|-------|------|--------|
| `premise-critical` | "What must be true"; TAM/SAM/SOM or internal cost-of-inaction; obtainable share; unit-economics hurdle that justifies a Must / `must-correct` | Until the evidence bar is met **or** the risk is recorded as `hold`. Converge-or-ask after 4 searches on the same claim. `market_type: internal` skips market-sizing searches entirely. |
| `supporting` | Named competitor, cited regulation, one pricing datapoint, one analogous case | 2 searches per claim |
| `color` | Flavor, analogy, non-blocking context | 0 — do not search |

### Evidence loop

After a `premise-critical` or `supporting` claim is stated:

1. Classify the claim. Do not search `color`.
2. Run searches within the class budget. Write each result as an `evidence` record in the ledger (status `supported` \| `refuted` \| `unknown`).
3. Run the re-decision sweep ([decision-ledger.md](../../../refs/planning/decision-ledger.md)).
4. **Stop** when the evidence bar is met **or** the residual risk is recorded (`hold`, assumption with `blocking` set, or `research_deferred` with a named bar). User saying "accurate" is not a stop.

Do not treat a search result as verified fact without writing the evidence record. Do not invent a TAM to pass the MRD section.

Falsification prompt (required on `premise-critical`): "What evidence would make this false?" If the user cannot name any, the condition is `vague` — record that; do not fabricate a threshold.

Option-generation prompt (required when a seat blocks): "Name two paths that still move an ES metric if this premise is wrong." Feed those into the comparison table. A legal-risk tier (`green`/`yellow`/`gray`/`red`) surfaces residual risk but does **not** substitute for this prompt — tier ≠ block.

## Verdict ladder

Non-terminal. Recorded in `session_state.viability[]` and, for ranked-leaf decisions, as a ledger rationale.

| Verdict | Meaning | Advance? |
|---------|---------|----------|
| `proceed` | Evidence bar met; no blocking dissent | Yes, if other gates pass |
| `proceed-with-conditions` | Proceed; named conditions become `flips_when` on the rationale | Yes; conditions live in the ledger |
| `pivot(option)` | Premise or scope reframed; `option` is a concrete alternative from the comparison table | Do not freeze; re-discover affected sections |
| `hold(evidence)` | Missing evidence is named; bar is explicit | Do not freeze; do not advance. Prepend VIABILITY HOLD. |
| `kill` | Pivot options exhausted **and** user confirms. Write revival trigger (`flips_when` on a `reject` rationale) and bury the item | Checkpoint; do not recycle the id |

`hold` names the missing evidence. `pivot` carries the concrete reframing — not "think harder". `kill` without a revival trigger is a protocol failure.

Binding at executive-summary and MRD. Advisory at BRD/PRD — still record; user may accept advisory `hold`/`kill` and proceed (banner still applied on binding-level `hold` only).

## Dissent

When seats disagree:

1. Record each seat's verdict separately. Do not average, vote, or pick the median.
2. The disagreement is the finding — surface it as a Gate 7 question.
3. User (or binding seat, if the user defers) chooses. Log `type: viability_verdict` ([goal-anchor.md](goal-anchor.md)) with the dissenting seats named in `text`.

Silent resolution of dissent is a gate failure.

## Internal vs external

| Test | `market_type: external` | `market_type: internal` |
|------|-------------------------|-------------------------|
| Premise (ES) | What must be true in the market for this to be worth doing | What must be true operationally (teams, hours, loaded cost, do-nothing) |
| Sizing (MRD) | TAM / SAM / SOM, evidence-backed, incumbent + do-nothing | Affected-teams × hours × loaded cost; **no TAM**. Build-vs-buy + do-nothing are mandatory |
| Investor seat | Seed (ES) / growth (MRD) applies market hurdle | Same seats apply **cost-of-inaction** and opportunity-cost hurdles |
| Search | Premise-critical market search allowed | Skip market-sizing search; search only for analogous internal cost or buy options |

An internal project that reports TAM/SAM/SOM is a protocol failure — the numbers are not the decision.

## Premise test (executive-summary)

During ES discovery, after posture confirm and `domain_context`, before freezing ES:

1. Sit founder/CEO, seed investor, and domain practitioner.
2. Produce the **What must be true** prose section — the smallest set of premises the rest of the cascade stands on. Do not mint an `ES-*` id for it.
3. Classify each premise (`premise-critical` / `supporting` / `color`) and run the evidence loop.
4. Record the **Viability verdict** as prose (`proceed` … `kill`). Binding. Do not mint an `ES-*` id for it.

Done: both sections present; verdict ≠ `hold` unless the user accepts the banner; rationales minted for any ranked ES leaves that depend on those premises.

## Gate 7 (every level)

After Gate 6, sit this level's roster. Run the conduct protocol on the level's load-bearing claims (Must / `must-correct` / Kano `basic`, plus anything the sweep enqueued). Write `viability[]` for this level. Binding at ES/MRD; advisory below.

Open `re_decision_queue` or unresolved binding `hold`/`kill` → do not freeze ([success-criteria.md](../../../refs/planning/success-criteria.md), [proactivity.md](proactivity.md)).
