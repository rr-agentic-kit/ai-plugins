# ideation

**Owner:** Problem-space brainstorm, Opportunity Solution Tree (OST), posture-gated assumptions, and pretotype/YODA demand tests — before L1 compose when the idea is not yet concrete.

**Load when:** Skill ideation gate fires (problem space without a concrete product idea), or user explicitly asks to brainstorm / map assumptions / design a pretotype. Skip when the user already brings a named product bet with a clear problem statement.

**Does not:** mint cascade item IDs, run Gates 1–7, write PRD features, or invent TAM. Durable outputs land as session artifacts; freeze later pins them via `artifact_refs` ([business-case-handoff.md](business-case-handoff.md)).

## When to run

| Signal | Action |
|--------|--------|
| Vague problem / opportunity, no solution shape | Run full path: severity → brainstorm → OST → assumptions → prioritize → pretotype if HI×HR |
| Concrete idea + clear who/pain | Skip ideation; start posture → executive-summary |
| `existence: existing` feature bet already capability-shaped | Light assumptions (VUVF-4) only; park capability experiments to Plan notes — no mandatory pretotype |
| User says "skip ideation" | Record decision in ledger (`type: decision`); proceed to L1 |

Run **before** first L1 compose. Do not interleave after MRD/BRD unless `--change` reopens problem framing.

## Problem severity × frequency

Before solution talk, lock the pain:

| Probe | Required output |
|-------|-----------------|
| Who | Named role / segment (not "users") |
| How often | Frequency band (daily / weekly / episodic / rare) with source or `hold` |
| Cost of inaction | What breaks, costs, or opportunities die if we do nothing — qualitative OK; fabricated $ illegal |

Reject "nice idea" framing. If who/frequency/cost cannot be named → AskQuestion; do not invent. Park unresolved as `open_holds` candidates for L1.

Log material framing choices as ledger assumptions/decisions (`refs/planning/decision-ledger.md`).

## Multi-perspective brainstorm

Required seats on every assumption pass (devil's-advocate, not consensus theater):

| Seat | Pressure |
|------|----------|
| **PM** | Outcome, segment, willingness-to-pay vs vanity demand, kill criteria |
| **Designer** | Usability, JTBD clarity, switching friction, trust |
| **Engineer** | Feasibility, dependency risk, build/buy/partner realism |

Each seat owes at least one challenge and one alternative (including "do nothing"). Binding viability still belongs to Gate 7 / expert panel — ideation surfaces candidates only.

## Opportunity Solution Tree

When the path is opportunity-shaped (not a single forced solution):

```
Desired outcome
  └── Opportunity (customer need / pain)
        └── Solution (approach)
              └── Experiment (test)
```

Rules:

1. One desired outcome per tree (ties to North Star later — do not invent the metric here).
2. Opportunities are needs, not features. Feature-shaped nodes → park to notes / Plan.
3. Solutions branch only after opportunities are ranked by severity × frequency.
4. Experiments attach to HI×HR assumptions (below), not to every leaf.
5. Persist `opportunity-tree.md` when this path runs.

## Assumptions (posture-gated)

Read `session_state.project_posture.existence` ([project-posture.md](project-posture.md)). If posture not confirmed yet, run posture first.

### Greenfield / new → 8 categories

| Category | Ask |
|----------|-----|
| **Value** | Do people care enough to change behavior? |
| **Usability** | Can the intended user succeed without heroics? |
| **Viability** | Does the business model / internal case close? |
| **Feasibility** | Can we build/operate this with known constraints? |
| **Ethics** | Harm, consent, fairness, regulatory line — named or explicit N/A |
| **GTM** | Can we reach buyers? Channel realism? |
| **Strategy & Objectives** | Aligns with stated goals / non-goals? |
| **Team** | Founder/team capability risk to execute? |

Ethics and Team may be `N/A` with rationale — silent skip is failure.

### Existing → VUVF-4 only

Value, Usability, Viability, Feasibility. Do not force Ethics/GTM/Strategy/Team catalogs unless the user opens them.

### Impact × Risk prioritization

Score each assumption **Impact** (if false, how bad?) × **Risk** (how uncertain?):

| Quadrant | Disposition |
|----------|-------------|
| **HI × HR** | Experiment — pair with a concrete test before treating as fact |
| **HI × LR** | Proceed — still record; do not bury |
| **LI × HR** | Reject / deprioritize — do not burn cycles |
| **LI × LR** | Defer — park; do not block L1 |

Every HI×HR row **must** name a test method (pretotype below, interview, or cheap evidence bar with date). Unpaired HI×HR → block advance to L1 compose.

Persist `assumptions.md` when the map is produced. Item-like labels in that file are session-local (`A-1`…); do not mint `ES-`/`MRD-`/`BRD-` ids here. On L1 compose, promote surviving premises into cascade items + ledger evidence.

## Pretotype / YODA

**Skin-in-the-game:** prefer signals where the subject pays time, money, reputation, or attention that costs them — not polite interest.

**YODA:** Your Own Data Affirms — own experiment evidence beats others' TAM analogies, blog benchmarks, or "market is huge" stories. Fabricated TAM stays illegal ([goal-anchor.md](goal-anchor.md)).

### Methods (pick cheapest that can falsify)

| Method | Signal |
|--------|--------|
| Landing page | Intent + optional email with clear CTA |
| Explainer video | Watch-through / reply asks |
| Email / outreach | Reply rate with a concrete ask |
| Pre-order / waitlist | Commitment (preferred over vanity clicks) |
| Concierge | Manual delivery of the outcome |

### XYZ statement

Frame every pretotype as:

> At least **X%** of **Y** will **Z**.

X/Y/Z must be observable. Missing any → rewrite before run.

### Willingness-to-pay vs demand

| Test type | Proves | Does not prove |
|-----------|--------|----------------|
| Demand (waitlist, concierge take-up) | Someone wants the outcome | Price they will pay |
| Pricing / pre-order with $ | Willingness-to-pay | Full retention |

Demand test ≠ pricing. Prefer pre-order/waitlist over click vanity. Pricing probes are optional and separate — do not collapse into one metric.

Persist `pretotype-brief.md` when framed (method, XYZ, kill/success bar, timebox). Not a launch plan — stop before calendars and campaign briefs ([gtm-framing.md](gtm-framing.md)).

## Artifacts

| File | When | Freeze link |
|------|------|-------------|
| `assumptions.md` | Assumption map produced | `artifact_refs.assumptions` |
| `opportunity-tree.md` | OST path used | `artifact_refs.opportunity_tree` |
| `pretotype-brief.md` | XYZ/pretotype framed | `artifact_refs.pretotype` |

Write under `--output-dir`. Human-facing prose through [compose-prose.md](compose-prose.md) when the skill persists them as session markdown. Machine pins stay in `business-case.yaml` / ledger.

## Done-when

- Severity × frequency named (or explicit `hold` with AskQuestion trail in raw-history)
- PM / Designer / Engineer seats recorded on the assumption pass
- Category set matches posture (8-cat or VUVF-4)
- Every HI×HR has a paired test
- Conditional artifacts on disk if those techniques ran
- Ready for posture (if not done) → executive-summary compose

## Further reading

Techniques adapted from phuryn/pm-skills (MIT): assumption catalogs, Impact×Risk quadrants, pretotype/YODA framing.
