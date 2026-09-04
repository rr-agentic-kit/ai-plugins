# business-case-handoff

**Owner:** Compact frozen handoff contract — `business-case.yaml` — that Plan (`rr-planner`) consumes. Not a cascade doc dump.

**Load when:** After BRD Gates 1–7 pass and the skill is ready to freeze discovery; also when validating Plan entry or repairing a missing handoff.

**Does not:** replace `executive-summary.md` / `mrd.md` / `brd.md`, mint PRD, or auto-advance Plan. Shared freeze/mint rules: [baselines.md](../../../refs/planning/baselines.md), [cascade.md](cascade.md).

## When handoff runs

After **BRD** completes Gates 1–7 with verdict `proceed` or `proceed-with-conditions`:

1. Mint level freeze for `brd` (and ensure ES/MRD already frozen) per [cascade.md](cascade.md) / [baselines.md](../../../refs/planning/baselines.md).
2. Write `{output_dir}/business-case.yaml` with required fields below.
3. Stamp `status.yaml` / session: `discovery_complete: true` (and digest pins as baselines require).
4. Require conditional artifacts on disk if those techniques ran ([ideation.md](ideation.md), [interview-method.md](interview-method.md)).
5. **Next Up:** Plan (`rr-planner`) — do not compose PRD inside Discover.

If Gate 7 is `hold` / `pivot` / `kill` → **do not** mint `discovery_complete`. Follow expert-panel verdict ladder.

## Required fields

| Field | Source | Notes |
|-------|--------|-------|
| `vision` | executive-summary | One durable vision statement |
| `problem` | executive-summary | Who / severity × frequency / cost of inaction |
| `premises` | what-must-be-true + claim-class | List; each ties to ledger evidence or explicit `hold` |
| `viability_verdict` | L1/MRD Gate 7 | `proceed` \| `proceed-with-conditions` \| … (must match ledger `viability_verdict`) |
| `north_star` | L1 metrics | Single North Star with metric teeth |
| `input_metrics` | L1 | ≤3 drivers of North Star |
| `omtm` | L1 (optional) | One metric that matters this quarter — omit or null if unused |
| `cost_position` | strategy lens / L1 | `low-cost` \| `unique-value` \| named hybrid |
| `defensibility` | L1 Can't/Won't | Why hard to copy — or explicit `hold` |
| `market_read` | MRD | Overview + primary segment + incumbent + do-nothing |
| `beachhead_icp` | MRD / GTM | Segment + why-first + ICP behaviors/JTBD/needs |
| `positioning_angle` | GTM (optional) | One line vs incumbent — or `hold` |
| `objectives` | BRD Must | Business objectives only |
| `stakeholders` | BRD | buyer / user / approver **plus** Power×Interest roles |
| `capabilities` | BRD | build / buy / partner (strategic — not architecture) |
| `constraints` | L1 + BRD | Hard boundaries (incl. consent / regulatory when present) |
| `non_goals` | L1 trade-offs | Explicit out-of-scope |
| `gtm_motion` | GTM framing | Strategy-level motion only (PLG / outbound / community / …) |
| `open_holds` | cascade + techniques | Explicit `hold` / `vague` sizing or deferred evidence bars |
| `artifact_refs` | session | Paths to conditional artifacts if present |
| `ledger_pins` | decision-ledger | Reserved rationale/evidence ids Plan must not recycle |

### `stakeholders` shape

Each entry minimally:

```yaml
- role: buyer|user|approver|other
  name_or_title: "…"
  power: high|medium|low
  interest: high|medium|low
  grid: manage_closely|satisfy|communicate|monitor
```

### `artifact_refs` shape

```yaml
artifact_refs:
  assumptions: assumptions.md        # if produced
  opportunity_tree: opportunity-tree.md
  interview_synthesis: interview-synthesis.md
  pretotype: pretotype-brief.md
```

Omit keys for techniques that never ran. If a technique **ran** and the file is missing → freeze **fails**.

### `ledger_pins`

List stable ids (`r-…`, evidence ids) that Plan must not recycle. Source of truth remains `decision-ledger.yaml` — pins are the handoff snapshot.

## Freeze failure conditions

Freeze / `discovery_complete` **fails** when any of:

| Condition | Why |
|-----------|-----|
| Required field missing or empty | Plan cannot enter safely |
| Success metric decorative | North Star / inputs lack decision teeth (cannot detect failure) |
| Fabricated TAM or fake precision economics | Illegal — use `hold` / `vague` instead |
| Conditional technique ran but artifact absent | Assumptions/OST/interview/pretotype must survive chat |
| BRD (or ancestor) not freeze-eligible | Gates 1–7 incomplete or verdict blocks |
| `viability_verdict` disagrees with ledger | Handoff must match Gate 7 record |

Fabricated market numbers remain illegal even if "required" — prefer honest `hold` in `open_holds` / premises.

## Machine file rules

- Path: `{output_dir}/business-case.yaml` (name constant for validator).
- **Skip** humanize ([compose-prose.md](compose-prose.md)).
- Not a cascade stem: no item ids, no Gates 1–7 against this file as a doc.
- Plan entry gate: refuse unless `brd` ∈ `frozen_levels` **and** this file present with required fields.

## Minimal skeleton

```yaml
vision: "…"
problem: "…"
premises:
  - id: P1
    text: "…"
    claim_class: assumption|fact
    status: open|accepted|hold
viability_verdict: proceed
north_star: "…"
input_metrics:
  - "…"
omtm: null
cost_position: unique-value
defensibility: "Can't: …; Won't: …"
market_read: "…"
beachhead_icp: "…"
positioning_angle: hold
objectives:
  - "…"
stakeholders:
  - role: buyer
    name_or_title: "…"
    power: high
    interest: high
    grid: manage_closely
capabilities:
  - choice: build|buy|partner
    what: "…"
constraints:
  - "…"
non_goals:
  - "…"
gtm_motion: plg
open_holds: []
artifact_refs: {}
ledger_pins: []
```

## Done-when

- YAML written; required fields populated or explicit legal `hold`s
- Conditional artifacts present iff techniques ran
- `discovery_complete` stamped
- User pointed at Plan — Discover stops
