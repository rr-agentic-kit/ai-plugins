# item-schema

**Owner:** Shared item identity, parent walk, atomic split, per-level priority/scoring methods, spec states, PRD requirement `priority` + selection `status`, Effort provenance, and parseable markdown. Numbering and status live here once — level standards keep section lists and done-when.

**Load when:** Discovering, composing, validating, or challenging any cascade doc.

Audience: compose agent + orchestrator. Working surface is markdown. Validation target is structured (`items.json`).

## Shared fields

Every numbered item has `id`, `parent`, `kind`, `spec`. Ranking fields depend on the **document type** (not a per-item choice). `status` and `priority` exist only on PRD leaves (selection + requirement priority — not derived from children).

| Field | Where | Values |
|-------|-------|--------|
| `id` | all | `{DOC}-{n}` or `{DOC}-{n.m}` — see Numbering |
| `parent` | all | Immediate parent item ID, or `—` for ES roots |
| `kind` | all | `container` \| `leaf` |
| `spec` | all | `idea` \| `draft` \| `ready` \| `deprecated` |
| `status` | PRD leaves only | `deferred` \| `selected` \| `in_progress` \| `delivered` — selection/delivery marker; no derivation; selecting never deletes the full requirement set |
| `priority` | PRD **requirement** leaves only | `P1` \| `P2` \| `P3` — priority inside a feature’s full set; coexists with RICE (features) / RIC (stories). No P-tags elsewhere (MoSCoW stays Discover-only) |
| `tag` | ES constraint leaves only | Open string (e.g. `regulatory`, `capacity`, `quality`, `technical`) — optional subtype hint |
| `goal_type` | PRD goal leaves only | `primary` \| `support` |
| `reach` | PRD story/feature leaves | Percentage string with named denominator (e.g. `40% of monthly active users`) |
| `impact` | PRD story/feature leaves | `0.25` \| `0.5` \| `1` \| `2` \| `3` |
| `confidence` | PRD story/feature leaves | `low` \| `medium` \| `high` |
| `effort` | PRD feature leaves only | Fibonacci `1` \| `2` \| `3` \| `5` \| `8` \| `13` — **same-sitting** with architecture for that capability (spine and/or feature delta) before score is real; see Effort provenance |
| `rationale` | ranked leaves | `r-\d{3,}` pointer into `refs/planning/decision-ledger.md`. Optional on containers. Required once the leaf has a real rank/score value. Never emit `_rationale_: —`. |
| `supersedes` / `superseded-by` | optional | Replacement pair (both ends or neither). JSON field remains `superseded_by`. |

Containers stay unmarked (no MoSCoW / Kano). Index tables show the level’s native field.

## Numbering

- ID: `{DOC}-{n}[.{n}]` with prefixes `ES`, `MRD`, `BRD`, `PRD`.
- **Mint `{DOC}-n` only for what the level ranks** (plus containers that group ranked leaves). Unranked narrative, already-labeled partitions, and context lists stay unnumbered prose. Numbering exists to (1) rank, (2) nest ranked children, (3) parent-walk. If none apply, the heading is prose. Do not invent semantic ids (`exec-vision`, `mrd-primary`, `prd-persona`).
- Continuous among **siblings** (`1, 2, 3` — no gaps at compose). Children of item 3 are `3.1`, `3.2`, … not new top-level numbers.
- Unique across the cascade because of the prefix (`PRD-3` ≠ `BRD-3`).
- Max depth **2** inside a document (`n.m`). Deeper means the parent is not a real grouping — split the parent into siblings.
- **Freeze / remap** (when IDs freeze, append-only inserts, re-compose rewrite): `skills/rr-planner/refs/cascade.md`. This ref owns ID shape, sibling density, and max depth.

Rejected: one global `1…N` across all four docs. Rejected: semantic names (`exec-vision`) — not continuous, do not nest.

## Parent pointer

Single field `parent:` = **immediate** parent item ID.

| Case | Value |
|------|-------|
| ES roots | `—` |
| Nested child (same doc) | `PRD-3` |
| Cross-doc (default) | `BRD-2` (previous cascade level) |
| Cross-doc (PRD exception, C2-7) | `ES-1` **or** `BRD-2` — ≥1 ES **or** ≥1 BRD parent (OR, not AND) |

Full chain is a walk: `PRD-4.1 → PRD-4 → BRD-2 → MRD-1.2 → MRD-1 → ES-1`. Success-criteria validates the walk. Docs do **not** repeat the whole chain on every item.

Cross-doc parent must be the previous cascade level (no skips) **except PRD**, which may parent directly to ES or BRD. Same-doc parent of `{DOC}-{n.m}` must be `{DOC}-{n}`.

## Atomic split

**One leaf = one testable statement.** A container has children and no `shall` of its own. A leaf has body and no children. Never both.

Split when a fact has multiple independent shalls, multiple actors, or a list of distinct outcomes. Example: “5 requirements for checkout” → `PRD-3` container + `PRD-3.1`…`PRD-3.5` leaves.

Prose overviews and unranked context (vision, posture, segments, personas, stakeholders, risks, sizing) stay unnumbered. Ranked claims — constraints, objectives, needs, rules, stories, features, requirements — are items. After compose, **no level has unranked leaves.** `—` is not a rank class. It is a placeholder for a field that belongs on this item but is not decided yet.

| `kind` | Same-doc children | Body |
|--------|-------------------|------|
| `container` | ≥1 | Grouping title only — no shall / AC |
| `leaf` | none | Statement |

**Kind invariant** is same-document nesting only. Cross-doc `parent:` is the cascade walk, not a child for `kind`.

An `idea` item must not have children (promote to `draft` first).

## Which sections are items

Declared per level. Native priority method is a property of the **document type**.

| Level | Prefix | Method | Rankable leaves | Prose (unnumbered) |
|-------|--------|--------|-----------------|--------------------|
| executive-summary | `ES` | MoSCoW on functional deliverables only | Why now, success metrics, functional deliverables, constraints (optional `tag`), non-goals, horizons (optional) | Posture, vision, problem, what-must-be-true, viability verdict |
| mrd | `MRD` | Kano | Customer needs | Market overview, TAM/SAM/SOM (or internal cost-of-inaction), target segments (`**Primary:**` / `**Secondary:**`), competitors, trends, risks |
| brd | `BRD` | MoSCoW | Objectives, rules, dependencies | Stakeholders (buyer / user / approver in the section), business risks (impact × likelihood bullets) |
| prd | `PRD` | RICE / RIC / goal-type + requirement P1–P3 | Goals (`primary`/`support`), stories (RIC), features (RICE), requirement leaves (`priority` + `status`), out-of-scope (no score) | Shape, product overview, user personas (named in story bodies), WWAS AC |

ES functional deliverables are Must-only in practice. ES constraints may carry optional `tag`. MRD segments state primary/secondary in the section (not a rank, not an id). MRD/BRD risks state impact × likelihood in the section. PRD `status` / `priority` are manual leaf fields — not derived from children.

### Emit: omit vs placeholder

Do not write keys that will never apply. Do not write `—` to mean “this field is not a thing.”

- **Omit** — empty by nature / inapplicable: containers have no `_moscow_` / `_kano_` / RICE keys (already `CONTAINER_RANK` if present). No `_status_` / `_priority_` except on PRD leaves (`priority` = requirement leaves only). No `_tag_` except on ES constraint leaves. No `_goal-type_` except on PRD goal leaves. No `_rationale_` until minted (never `_rationale_: —`). No method key on a heading that is not an item.
- **Placeholder `—`** — expected on this item, not yet decided: ranked leaf still `idea`/`draft` without a value → `_moscow_: —`, `_kano_: —`, or RICE factor `—`. Drop the key once the real value is written.
- **Ready** — real rank/score required where the section demands it. `spec: ready` + missing required method key or `—` is `DOR`, not an unranked item.

`—` = null for an applicable key not yet decided; omit inapplicable keys. `_parent_: —` on ES roots stays (graph null, not a rank).

### Per-level methods

Do not apply one ranking system to the whole cascade. No 1–5. **No P-tags except PRD requirement leaves** (`P1`/`P2`/`P3`). MoSCoW stays Discover-only.

- **executive-summary — MoSCoW on functional deliverables only.** Posture, vision, problem, what-must-be-true, and viability verdict are **prose** (no `ES-*` id). Why now, success metrics, constraints, non-goals, and horizons are ranked leaves **without** MoSCoW. Functional deliverables are Must-only in practice (MoSCoW rank). Constraints may carry optional `_tag_:` (`regulatory`, `capacity`, `quality`, `technical`, …).
- **mrd — Kano on needs** (`basic` / `performance` / `delighter`). Why: market needs are about satisfaction-if-present vs dissatisfaction-if-absent; MoSCoW flattens delighters into Could.
- **brd — MoSCoW on objectives, rules, and dependencies.** Compliance/contractual rules are Must. Why: business-negotiation language for cutting scope. MoSCoW legend: Discover `skills/rr-discovery/refs/project-posture.md`.
- **prd — RICE/RIC backlog + requirement priority + selection.** Goals: `_goal-type_: primary | support`. Stories: RIC (`reach`, `impact`, `confidence` — no `effort`). Features: full RICE (`reach`, `impact`, `confidence`, `effort` Fibonacci 1,2,3,5,8,13). Requirement leaves: `_priority_: P1|P2|P3` plus optional `_status_:` (`deferred` \| `selected` \| `in_progress` \| `delivered`). Out-of-scope: no RICE. Composed score not stored. Cross-doc parent: ≥1 ES **or** ≥1 BRD (C2-7). Plan mechanism/AC lives in standing architecture + feature deltas + WWAS AC — **not** root `tech.md` (`refs/planning/output-formats.md`). Discover may still park early mechanism notes in `tech.md`.

### Effort provenance (PRD features)

`_effort_:` is real only when an architecture decision for that capability exists **in the same Plan pass** (standing spine update and/or `docs/plan/deltas/<feature-id>.md`). Refuse Effort-without-architecture. Fibonacci remains a relative size, not sprint capacity.

## Spec (agreement axis)

`idea` → `draft` → `ready` → `deprecated`

| State | Meaning | Implement? |
|-------|---------|------------|
| `idea` | Inbox. Captured, existence **not** committed, **not** being authored. Parked. | no |
| `draft` | Spec WIP. Existence committed; fields may be incomplete; writing/splitting/clarifying. | no |
| `ready` | DoR met **and** explicitly approved. | yes (when dev workflow starts) |
| `deprecated` | Do not implement; keep for history. | no |

Skip `draft` when the item arrives complete: `idea → ready` is legal. Do not require a fake WIP hop.

Containers have `spec` only. A container may stay `draft` while one child is `ready`. **Only leaves are implementable.**

Legal transitions: `idea → draft|ready|deprecated`; `draft → ready|idea|deprecated`; `ready → draft` (reopen) `| deprecated`; `deprecated` terminal (revive = new id).

Discovery defaults new items to `idea`. Moving to `draft` means “we are specifying this now.” Compose does **not** auto-promote to `ready` because fields exist — promotion is a user/gate action.

### DoR (code gates)

| Rule | Effect |
|------|--------|
| `spec == ready` | Real rank/score present where required (`—` does not count). Cross-doc parent must be `ready`. Same-doc container is exempt. PRD cross-doc parent may be ES or BRD. |
| `deprecated` | Keep for history; revival requires a new id |
| Replacement | New item starts `spec: draft` (or `idea`). Old item `spec: deprecated` as soon as the successor exists |
| `idea` children | FAIL if an `idea` item has children |
| Depth | `shallow`: one-liners may be assumptions. `standard`/`deep`: blocking if a **ready** leaf is missing a real rank (`—` does not count) |

### Example mapping

- Feature scored, approved: `PRD-4.1 spec:ready _reach_: 60% of MAU | _impact_: 2 | _confidence_: medium | _effort_: 5`. Story still fuzzy: `PRD-4.2 spec:draft`. Container `PRD-4 spec:draft`.
- Selected requirement: `PRD-4.1.1 spec:ready _priority_: P1 | _status_: selected` (full set kept; siblings may stay `_status_: deferred`).
- Shipped leaf: `PRD-4.1.1 … _status_: delivered` (manual marker).
- ES consent constraint: `ES-5 spec:ready _tag_: regulatory` (no MoSCoW).
- Replace a requirement: `PRD-4.1.1 spec:deprecated superseded_by:PRD-9`; `PRD-9 spec:draft supersedes:PRD-4.1.1` until user promotes `ready`.

## Canonical item surface (closed vocabulary)

Working surface is markdown. Validation target is structured. Compose writes `{level}.md` and merges `items.json`. Item records live on disk, not in the Task return. Cascade `{stem}.yaml` and list-meta (`- **Key:**`) are stale — `validate_planning.sh --rewrite` migrates them.

Parser is regex, not an LLM. Three-line grammar:

1. Heading = id + title
2. Next non-empty line = closed metadata (`_key_:`)
3. Following `^> ?` lines = body; anything else before the next heading is prose or `STALE_FORMAT`. Leaf body without `>` is `BODY_NOT_BLOCKQUOTE`. Containers have no `>` body.

Heading:

```
^(#{2,4}) (ES|MRD|BRD|PRD)-(\d+(?:\.\d+)?): (.+)$
```

Metadata — one line immediately under the heading. Keys are hyphenated (`_if-present_`, `_superseded-by_`), not snake_case, so wrapping `_key_:` renders as one italic span.

```
_parent_: PRD-3 | _kind_: leaf | _spec_: ready | _reach_: 60% of MAU | _impact_: 2 | _confidence_: medium | _effort_: 5 | _rationale_: r-014
```

Split segments on `\s+\|\s+(?=_[a-z][a-z0-9-]*_:)` so effect text may contain `|`. FAIL if a segment is not `_key_: value` or the key is unknown/duplicate.

| Keys (md surface) | Who | Internal / `items.json` |
|-------------------|-----|-------------------------|
| **Required (all items)** | `parent`, `kind`, `spec` | same |
| **Ranked leaves also** | `rationale` (`r-NNN`, minted in the ledger before compose prints it) | `rationale` |
| **PRD leaves also** | `status` (`deferred` \| `selected` \| `in_progress` \| `delivered`) | `status` |
| **PRD requirement leaves also** | `priority` (`P1` \| `P2` \| `P3`) | `priority` |
| **PRD goal leaves also** | `goal-type` (`primary` \| `support`) | `goal_type` |
| **PRD story/feature leaves also** | `reach`, `impact`, `confidence`; `effort` on features only | same |
| **ES constraint leaves also** | `tag` (open string, e.g. `regulatory`) | `tag` |
| **Leaves, native method** | `moscow` (ES functional deliverables, BRD) \| `kano` (MRD) | `moscow` \| `kano` |
| **Optional** | `supersedes`, `superseded-by`; `rationale` on containers | `supersedes`, `superseded_by` |

Canonical emit order: `parent, kind, spec, status, priority, tag, goal-type, reach, impact, confidence, effort, moscow, kano, rationale, supersedes, superseded-by`. Omit inapplicable keys. `--rewrite` must not inject method `—` when the source omitted the key. Emit only keys present on the item (plus required `parent`/`kind`/`spec` for a parseable header).

Unknown keys or missing required keys (`parent`, `kind`, `spec`) → validator FAIL. Body is the blockquote (AI-judged). `idea`/`draft` leaves may omit method/score keys or emit `—`. `ready` leaves missing a **real** rank/score where required (`—` does not count) → `DOR`.

`_parent_: —` means graph null (ES roots). Native rank `—` means “applicable, not yet decided.”

JSON shape: `refs/planning/schemas/items.schema.json`. Graph checks: `scripts/validate_planning.sh` (md-only; `--format yaml|json` is `UNSUPPORTED_FORMAT`).

**Code owns:** unique IDs, parent/supersede pointers, numbering density, kind invariant, required keys, status legality, doc/`items.json` drift, rationale id shape and resolution against `decision-ledger.yaml`.

**AI owns:** whether a leaf is actually atomic, whether MoSCoW is inflated, whether the shall is testable, whether a `flips_when` condition is well-chosen (never a script FAIL).

## Templates

### Container (any level)

```markdown
### PRD-3: Checkout
_parent_: BRD-2 | _kind_: container | _spec_: draft
```

### Leaf — MoSCoW (ES functional deliverables / BRD)

```markdown
#### ES-3: Multi-language support
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-007

> Product UI and content available in English and Spanish at launch.
```

```markdown
#### BRD-2.1: Revenue share cap
_parent_: BRD-2 | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-014

> Partner revenue share shall not exceed 30% without executive approval.
```

### Leaf — Kano (MRD needs)

```markdown
#### MRD-2.1: Checkout without an account
_parent_: MRD-2 | _kind_: leaf | _spec_: ready | _kano_: basic | _rationale_: r-002
```

### Leaf — ES constraint with tag

```markdown
#### ES-5: GDPR consent for personalization
_parent_: — | _kind_: leaf | _spec_: ready | _tag_: regulatory | _rationale_: r-009

> Consent required before collecting taste profile or feedback data; users can see, delete, and change consent.
```

### Leaf — PRD goal

```markdown
#### PRD-1: Increase first-purchase conversion
_parent_: BRD-2 | _kind_: leaf | _spec_: ready | _goal-type_: primary | _rationale_: r-010

> Move checkout completion rate from 12% to 18% within 90 days of launch.
```

### Leaf — PRD story (RIC)

```markdown
#### PRD-3.1: Guest checkout story
_parent_: PRD-3 | _kind_: leaf | _spec_: ready | _reach_: 40% of first-time visitors | _impact_: 2 | _confidence_: medium | _rationale_: r-014

> As a guest, I can complete checkout without an account so that first purchase is not blocked.
```

### Leaf — PRD feature (RICE)

```markdown
#### PRD-3: Guest checkout
_parent_: BRD-2 | _kind_: leaf | _spec_: ready | _reach_: 40% of first-time visitors | _impact_: 2 | _confidence_: medium | _effort_: 5 | _rationale_: r-014

> Enable checkout without account creation for first-time buyers.
```

### Leaf — PRD feature (RICE + selection)

```markdown
#### PRD-3: Guest checkout
_parent_: BRD-2 | _kind_: leaf | _spec_: ready | _reach_: 40% of first-time visitors | _impact_: 2 | _confidence_: medium | _effort_: 5 | _status_: selected | _rationale_: r-014

> Enable checkout without account creation for first-time buyers.
```

### Leaf — PRD requirement (P-priority + selection)

```markdown
#### PRD-3.1: Guest may pay without account
_parent_: PRD-3 | _kind_: leaf | _spec_: ready | _priority_: P1 | _status_: selected | _rationale_: r-015

> Guest completes payment without creating an account; account optional after purchase.
```

## Item index

Each composed markdown file ends with an index. Column 4 is the level’s native field (`MoSCoW` / `Kano` / `RICE` / `RIC` / `Goal`). Containers show `—` in the method column because they have no rank, not because they are unranked leaves.

```markdown
## Item index

| ID | Parent | Spec | RICE |
|----|--------|------|------|
| PRD-3 | BRD-2 | draft | — |
| PRD-3.1 | PRD-3 | ready | R:40% I:2 C:med |
```
