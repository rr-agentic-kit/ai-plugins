# decision-ledger

**Owner:** `decision-ledger.yaml` — evidence, rationales, graveyard, reserved ids, and the re-decision queue. Justification-based truth maintenance: items rest on rationales, rationales rest on evidence; when evidence flips, dependents are **raised for re-decision**, never auto-demoted.

**Load when:** Minting a rationale during discovery; every sweep trigger; compose (read `reserved_ids` only); challenge (read-only scan); Gate 7 and pre-save. Skill owns the file. Compose and challenge never write it.

This file is **validator input** — unlike `{level}.notes.yaml`. `validate_planning.sh` resolves rationale pointers. Structure only: the id resolves, `flips_when` is non-empty, `kind` is in the enum, `evidence:` pointers resolve. Whether a condition is well-chosen is AI judgment ([success-criteria.md](success-criteria.md)).

## Boundary vs goal-anchor

| Concern | Owner |
|---------|-------|
| Unclear vs ambiguous input; clarify-before-assume; nuance; goal re-anchor; `decisions[]` / `assumptions[]` in `session-state.json` | [goal-anchor.md](../../skills/rr-planner/refs/goal-anchor.md) |
| Evidence records, rationale graph, `flips_when`, burial, reserved ids, re-decision queue | This ref |

Do not put rationale bodies, evidence claims, or `flips_when` in the decision log. Log `type: rationale` / `re_decision` / `revival` / `viability_verdict` as the human-facing pointer (`text` may cite `r-014`); the graph lives here.

Compose never writes this file — same boundary that keeps it out of `session-state.json` and the notes sidecars.

## File

Always YAML. Path: `{output-dir}/decision-ledger.yaml`. Skill creates it at first rationale mint (typically ES premise test). Missing file → validator `WARN [LEDGER_MISSING]`; rationale checks skipped (legacy dirs). Once present, the skill always writes it and the validator enforces fully.

```yaml
version: 1
evidence:
  e-001:
    claim: "Obtainable share reaches 10% by year 3"
    status: refuted          # supported | refuted | unknown | superseded
    confidence: high         # high | medium | low
    sources:
      - { title: "...", url: "https://...", accessed: 2026-08-16 }
    superseded_by: e-014     # optional; required when status is superseded
rationales:
  r-014:
    decision: accept         # accept | reject | postpone | pivot
    subject: PRD-4
    seat: growth-investor
    because: "Payback only above 5% obtainable share"
    depends_on: [e-001, a-003]
    flips_when:
      - { kind: metric, metric: obtainable_share, op: "<", value: 0.05 }
      - { kind: fact, evidence: e-001, becomes: refuted }
      - { kind: event, text: "Incumbent unbundles this and ships it free" }
    condition_strength: measurable   # measurable | observable | vague
    status: live             # live | invalidated | superseded
graveyard:
  PRD-4:
    title: "Enterprise SSO in v1"
    snapshot: { kind: leaf, spec: ready, moscow: Must }
    rationale: r-014
    killed: 2026-08-16T12:00:00Z
reserved_ids:
  prd: [4]
re_decision_queue:
  - rationale: r-014
    trigger: "e-001 refuted"
    affected: [PRD-4, PRD-9]
    status: open             # open | decided | dismissed
```

Ids: evidence `e-\d{3,}`, rationales `r-\d{3,}`, monotonic, never recycled. `depends_on` may point at `e-*` (this file) or `a-*` (session-state assumptions). Validator resolves `e-*` in `flips_when` `fact` entries; it does not load `session-state.json` for `a-*`.

## Minting

Sequencing: the rationale is minted **during discovery at the moment the decision is made**, the skill writes the ledger, **then** compose references the id. Ranked leaves carry `Rationale: r-014`. Containers may omit it. Prose sections (vision, posture, personas, segments, what-must-be-true, viability verdict) are not items — they do not take `Rationale`.

| Rule | Detail |
|------|--------|
| When | User (or binding panel) accepts, rejects, postpones, or pivots a ranked leaf |
| Who writes | Skill. Compose reads `r-*` from `level_facts` and prints the closed key; it does not mint |
| Required fields | `decision`, `subject`, `seat`, `because`, `depends_on` (may be empty list only if `flips_when` has an `event`), `flips_when` (≥1), `condition_strength`, `status: live` |
| `seat` | Roster id from [expert-panel.md](../../skills/rr-planner/refs/expert-panel.md) (e.g. `growth-investor`, `domain-practitioner`) |
| Never | Invent `r-*` at compose time; point a ranked leaf at an id not yet in this file |

`decision` gives the sense of `flips_when`: the same list **invalidates** an `accept` and **revives** a `reject`. One list, both directions.

## `flips_when`

Conditions are **not** required to be numeric. Three kinds; one list.

| `kind` | Shape | Who evaluates |
|--------|-------|----------------|
| `metric` | `{ kind: metric, metric: <name>, op: <\|<=\|>\|>=\|==\|!=, value: <number\|string> }` | Sweep, mechanically |
| `fact` | `{ kind: fact, evidence: e-NNN, becomes: supported\|refuted\|unknown\|superseded }` | Sweep, mechanically |
| `event` | `{ kind: event, text: "<observable world condition>" }` | Panel judgment |

### `condition_strength`

| Value | Meaning |
|-------|---------|
| `measurable` | A number or dated metric the sweep can evaluate |
| `observable` | A world condition a practitioner would recognize (typical `event`) |
| `vague` | Honest "we'll know it when we see it" — allowed, never preferred |

**Never invent a number to satisfy the shape.** A fabricated threshold is worse than an honest qualitative condition: the fabricated one passes the sweep silently and wrongly. Measurable is a preference the seat pushes for, not a gate. A Must or `must-correct` item resting on `vague` is a judgment finding ([success-criteria.md](success-criteria.md)) — never a script FAIL.

## Two-tier sweep

Invalidation **raises a queue**. It never auto-flips `spec`, MoSCoW, or `decision`. Silent auto-demotion would make the plan unstable under every new search result and strip the user out of the decision they care about.

| Tier | Conditions | When | Output |
|------|------------|------|--------|
| Mechanical | `metric`, `fact` | Every trigger | Mark matching rationales `invalidated`; enqueue affected items with a panel recommendation (`postpone` / `kill` / `revive` / `keep`) |
| Judgment | `event` | New evidence in that area, or explicit request | Surface "worth re-checking" — not a definite flip |

Walk `depends_on` **backward** from changed evidence. Enqueue the rationale's `subject` and same-doc / cross-doc descendants (challenge and Gate 7 consume the queue). Status on the item does not change until the user (or binding panel) decides.

### Triggers (always all four)

1. After every evidence round ([expert-panel.md](../../skills/rr-planner/refs/expert-panel.md) evidence loop; also research findings that write evidence records).
2. On cascade **level entry**.
3. On `--resume`.
4. At **pre-save** ([proactivity.md](../../skills/rr-planner/refs/proactivity.md)).

Open queue or unresolved binding `hold`/`kill` blocks freeze and pre-save persist of `final_status: ok`.

## Kill / postpone cascade

Killing or postponing an item surfaces its **same-doc children** and **cross-doc descendants** and requires a decision for each: `kill`, `re-parent`, or `keep`.

| Step | Who | Action |
|------|-----|--------|
| 1. Decide | Panel + user | `kill` or `postpone` on the subject; mint/update the rationale (`decision: reject` or `postpone`) |
| 2. Dependents | Skill | List children/descendants; sit the question per item — do not silently cascade |
| 3. Bury (kill only) | Skill | Snapshot into `graveyard`; append the numeric id to `reserved_ids` for that doc prefix; drop the item from `level_facts` |
| 4. Re-compose | Compose | Reads `reserved_ids`; never re-mints a buried id; omits the item; returns `items_removed[]` |
| 5. Graph | Compose | Item leaves `items.json`. Parent walks stay valid because descendants were re-parented, killed, or kept. Ids are never recycled |

Postpone keeps the item in `items.json` with `spec` unchanged until the re-decision; the queue entry stays `open`. Kill removes it. Revival of a killed item is a **new id** plus `type: revival` pointing at the graveyard snapshot — deprecated/killed ids stay reserved.

`reserved_ids` map: doc stem → list of integers (and `n.m` pairs as strings when a nested id was buried). Compose's mint skips those numbers.

## Challenge

Challenge loads this file read-only:

- Items whose live rationale `depends_on` evidence now `refuted` (or a `fact` condition that already holds).
- Graveyard / `reject` rationales whose `flips_when` now holds (revival candidates).

Findings only; do not mutate the ledger.

### User-confirmed scope changes (T2-3)

A user-confirmed `demote` or `scope_change` needs only **one honest `because`** tied to a surfaced challenge finding. The skill never demands more once the finding trail is complete — an incomplete finding trail, not a thin rationale, is the real failure mode.

### Re-litigation guard (T6-5, O4 TTL)

`hold` + dissent on a resolved `r-*` / `a-*` stops re-litigation in the same track. A later challenge finding on the same topic needs **new evidence** or downgrades to `low`.

The guard lapses **only** on an explicit `project_posture` change (existence or commitment axis flip) — not on a new challenge run or elapsed time. Lapsing **re-opens the question** for a fresh look; it does **not** reverse the prior resolution.

## Validator surface

`validate_planning.sh`: `LEDGER_MISSING` (warn, skip), `LEDGER_MALFORMED` (structure), `MISSING_RATIONALE` (ranked leaf, ledger present), `BROKEN_RATIONALE` (dangling id or unresolved `evidence:` pointer). Closed key and JSON field: [item-schema.md](doc-standards/item-schema.md).

## Resume

Do not dump the ledger into chat. Summarize: open queue count, invalidated rationales, revival candidates. Then drain or explicitly defer.
