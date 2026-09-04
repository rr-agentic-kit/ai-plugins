# strategy-lenses

**Owner:** Choose and apply a strategy lens (canvas / SWOT / value proposition / rough economics) so Discover can name cost position, trade-offs, and monetization honesty — without a mandatory sixth canvas file.

**Load when:** L1 strategy / viability sections need structure; Gate 7 or stage-exit asks for cost position / defensibility; user requests Lean / BMC / SWOT / VP canvas. Skip inventing a full canvas when posture is `existing` + internal platform and the user already has objectives — fill only the gaps Gate 7 needs.

**Does not:** write launch plans, PRD capabilities detail, or fabricate unit economics. Fills stay **inside the cascade section that asked for them** or a short appendix in that doc.

## Decision table — which lens

| Situation | Default lens | Why |
|-----------|--------------|-----|
| Venture / external product, early | **Startup Canvas** | Nine strategy blocks + cost/revenue — default venture lens |
| Need speed on falsifiable bets | **Lean Canvas** | Problem/solution/metrics/UVP/channels/costs/revenue as hypotheses |
| Business shape already settled | **Business Model Canvas (BMC)** | Partners, activities, resources, value, relationships, channels, segments, costs, revenues |
| Positioning vs environment | **SWOT** (on demand) | Strengths/Weaknesses/Opportunities/Threats — not a substitute for Startup Canvas |
| Outcome clarity without full canvas | **Value proposition (6-part JTBD)** (on demand) | Who/Why/What-before/How/What-after/Alternatives |
| Internal platform (`market_type: internal`) | Light Lean or objectives-only | No TAM theater; cost-of-delay / capacity already in MRD sizing |

`project_posture.existence: greenfield` prefers Startup Canvas. `existing` prefers gap fill on the settled shape (BMC or targeted cards) — not a greenfield redo.

Never require all lenses. One primary lens + optional VP card is enough for freeze.

## Startup Canvas (default venture)

Cover these blocks as **hypotheses or facts** (mark which). Map into executive-summary / MRD / BRD sections — do not create `startup-canvas.md` as a mandatory artifact.

| Block | Lands in |
|-------|----------|
| Problem / customer segments | L1 problem + MRD segments / beachhead |
| Unique value / unfair advantage | L1 differentiation + Can't/Won't defensibility |
| Solution (high level) | L1 — outcome-shaped, not PRD features |
| Channels | GTM motion ([gtm-framing.md](gtm-framing.md)) |
| Revenue / cost structure | Rough economics (below) + `cost_position` |
| Key metrics | North Star + ≤3 input metrics + optional OMTM |
| Key partners / activities / resources | BRD capabilities: build / buy / partner |

## Lean vs BMC

| Lens | Use when | Stop when |
|------|----------|-----------|
| Lean | Unknowns dominate; need kill-fast hypotheses | You start writing epics/stories |
| BMC | Model is known; documenting how money/value flows | You invent partners/channels with no evidence |

## Value proposition — 6-part JTBD (on demand)

| Part | Prompt |
|------|--------|
| **Who** | Customer / user in a situation |
| **Why** | Job / progress sought |
| **What-before** | Current unsatisfactory state |
| **How** | Our approach (mechanism-light) |
| **What-after** | Success state |
| **Alternatives** | Status quo + named incumbents |

Wire interview outputs ([interview-method.md](interview-method.md)) when available. Park feature detail to Plan.

## Rough economics + relative cost position

Required honesty for freeze (external ventures):

| Element | Done-when |
|---------|-----------|
| **Relative cost position** | `low-cost` **or** `unique-value` (or hybrid named) — not silent |
| **Payback / CAC–LTV sketch** | Order-of-magnitude ranges **or** explicit `hold` |
| **Internal** | Cost-of-delay / capacity trade — not fake SaaS LTV |

Rules:

1. Fabricated TAM / precision economics → illegal. Prefer `hold` / `vague` with evidence bar.
2. Decorative metrics (vanity without decision teeth) → fail freeze ([business-case-handoff.md](business-case-handoff.md)).
3. Economics narrative goes in L1 / MRD prose or appendix — handoff stores `cost_position` + `open_holds`, not a spreadsheet dump.

## Where fills live

| Output | Location |
|--------|----------|
| Canvas answers | Cascade section or short appendix in `executive-summary.md` / `mrd.md` / `brd.md` |
| North Star / OMTM / cost position / Can't/Won't | L1 + `business-case.yaml` fields |
| Build vs buy vs partner | BRD capabilities → `capabilities` handoff |
| Full SWOT / Lean / BMC file | **Not required.** Optional appendix only if user asks to keep a copy |

## Done-when

- Primary lens chosen (or explicit skip with rationale for internal/existing)
- Relative cost position named
- Economics sketch or `hold`
- No orphan sixth mandatory canvas file
- Defensibility (Can't/Won't) addressed or `hold` for Gate 7

## Further reading

Techniques adapted from phuryn/pm-skills (MIT): Startup Canvas default, Lean vs BMC lens compare, 6-part value proposition.
