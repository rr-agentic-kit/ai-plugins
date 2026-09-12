# gtm-framing

**Owner:** Beachhead segment, ICP, motion fit, light positioning, reachability, and switching trigger — strategy-level GTM only.

**Load when:** MRD competitive / segments work, L1 "why this customer first", or freeze needs `beachhead_icp` / `gtm_motion` / `positioning_angle`. Soft-skip for pure internal platforms with no external buyer — still name the internal beachhead adopter if rollout risk matters.

**Does not:** launch calendars, campaign plans, battlecards, growth-loop execution, or full persona journey maps. Those are Plan / GTM execution — `OUT_OF_SCOPE` for Discover.

## Beachhead segment

Pick **one** primary segment to win first.

| Probe | Required |
|-------|----------|
| Segment name | Specific (industry × size × role or equivalent) — not "SMB" alone |
| Why this segment first | Urgency, reachability, willingness, reference potential — at least one hard reason |
| Explicit non-beachheads | Who we are **not** chasing yet (ties to non-goals) |

If multiple segments look equal → AskQuestion. Do not silently average them into a fake beachhead.

## ICP (ideal customer profile)

Behaviors / JTBD / needs — not a novel-length persona.

| Dimension | Capture |
|-----------|---------|
| **Behaviors** | What they already do (tools, workarounds, buying motion) |
| **JTBD / needs** | Progress sought; push/pull if interview-backed |
| **Buyer vs user** | Who pays / who uses / who approves (align with BRD Power×Interest) |
| **Disqualifiers** | Who looks like a customer but is not |

Full journey maps and avatar essays are optional research artifacts — **not** freeze-required. ICP checklist + beachhead suffice.

## Motion fit (stop before launch)

Name the **primary** go-to-market motion that matches beachhead reachability:

| Motion (examples) | Fit signal |
|-------------------|------------|
| PLG / product-led | Self-serve trial; low-touch expansion |
| Outbound / sales-led | High ACV; needs human discovery |
| Community / bottoms-up | Peer networks; champions |
| Partner / channel | Distribution owned elsewhere |
| Internal adoption | Mandate + enablement (internal `market_type`) |

Record one primary (+ optional secondary). **Stop** before: launch week plans, content calendars, ad budgets, enablement playbooks.

## Positioning angle (light)

One line vs a **named** incumbent or status quo — not a marketing campaign.

| Good | Bad |
|------|-----|
| "For ops leads drowning in spreadsheet handoffs, unlike Spreadsheet+Email, we…" | Generic "better UX" with no incumbent |
| Explicit `hold` until competitive scan exists | Invented category leadership claims |

Store as optional `positioning_angle` on handoff — `hold` is legal; fabricated differentiation is not.

## Reachability / distribution blockers

| Ask | Outcome |
|-----|---------|
| Can we access beachhead buyers with a known channel? | Yes + channel named, or blocker listed |
| What blocks distribution? | Constraint, non-goal, or `open_holds` |

Unreachable beachhead → change segment or mark viability risk for Gate 7. Do not paper over with TAM.

## Switching trigger vs status quo

Why leave the incumbent / do-nothing?

| Capture | Rule |
|---------|------|
| Trigger | Event, cost, risk, or mandate that makes change necessary |
| Or `hold` | Explicit — stage-exit / Gate 7 must not silently skip |

Compliments and "innovation" are not triggers.

## Handoff mapping

| Field | Source |
|-------|--------|
| `beachhead_icp` | Segment + why-first + ICP behaviors/JTBD/needs |
| `gtm_motion` | Primary motion only |
| `positioning_angle` | One-liner or `hold` |
| `market_read` | Overview + primary segment + incumbent + do-nothing (MRD) |
| `open_holds` | Reachability / switching / positioning holds |

## Done-when

- Beachhead + why-this-first recorded
- ICP behaviors/JTBD/needs (or explicit thin-ICP with `hold`s)
- Motion named; no launch calendar
- Positioning angle or `hold`
- Switching trigger or `hold`
- Reachability addressed or blocked into constraints / holds

## Further reading

Techniques adapted from phuryn/pm-skills (MIT): beachhead segment, ICP checklist, motion fit, light positioning.
