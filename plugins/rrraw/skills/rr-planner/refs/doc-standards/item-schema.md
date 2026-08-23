# item-schema

**Owner:** Shared item identity, parent walk, atomic split, per-level priority methods, spec states, optional PRD `status`, and parseable markdown. Numbering and status live here once — level standards keep section lists and done-when.

**Load when:** Discovering, composing, validating, or challenging any cascade doc.

Audience: compose agent + orchestrator. Working surface is markdown. Validation target is structured (`items.json`).

## Shared fields

Every numbered item has `id`, `parent`, `kind`, `spec`. Priority fields depend on the **document type** (not a per-item choice). `status` exists only on PRD leaves (manual delivery marker — e.g. `delivered`).

| Field | Where | Values |
|-------|-------|--------|
| `id` | all | `{DOC}-{n}` or `{DOC}-{n.m}` — see Numbering |
| `parent` | all | Immediate parent item ID, or `—` for ES roots |
| `kind` | all | `container` \| `leaf` |
| `spec` | all | `idea` \| `draft` \| `ready` \| `deprecated` |
| `status` | PRD leaves only | Open string (e.g. `delivered`) — set directly by user/dev workflow; no derivation |
| `rationale` | ranked leaves | `r-\d{3,}` pointer into [decision-ledger.md](../decision-ledger.md). Optional on containers. Required once the leaf has a real rank value. Never emit `_rationale_: —`. |
| `supersedes` / `superseded-by` | optional | Replacement pair (both ends or neither). JSON field remains `superseded_by`. |

Containers stay unmarked (no MoSCoW / Kano). Index tables show the level’s native field.

## Numbering

- ID: `{DOC}-{n}[.{n}]` with prefixes `ES`, `MRD`, `BRD`, `PRD`.
- **Mint `{DOC}-n` only for what the level ranks** (plus containers that group ranked leaves). Unranked narrative, already-labeled partitions, and context lists stay unnumbered prose. Numbering exists to (1) rank, (2) nest ranked children, (3) parent-walk. If none apply, the heading is prose. Do not invent semantic ids (`exec-vision`, `mrd-primary`, `prd-persona`).
- Continuous among **siblings** (`1, 2, 3` — no gaps at compose). Children of item 3 are `3.1`, `3.2`, … not new top-level numbers.
- Unique across the cascade because of the prefix (`PRD-3` ≠ `BRD-3`).
- Max depth **2** inside a document (`n.m`). Deeper means the parent is not a real grouping — split the parent into siblings.
- **Freeze / remap** (when IDs freeze, append-only inserts, re-compose rewrite): [cascade.md](../cascade.md). This ref owns ID shape, sibling density, and max depth.

Rejected: one global `1…N` across all four docs. Rejected: semantic names (`exec-vision`) — not continuous, do not nest.

## Parent pointer

Single field `parent:` = **immediate** parent item ID.

| Case | Value |
|------|-------|
| ES roots | `—` |
| Nested child (same doc) | `PRD-3` |
| Cross-doc | `BRD-2` (previous cascade level only) |

Full chain is a walk: `PRD-4.1 → PRD-4 → BRD-2 → MRD-1.2 → MRD-1 → ES-1`. Success-criteria validates the walk. Docs do **not** repeat the whole chain on every item.

Cross-doc parent must be the previous cascade level (no skips). Same-doc parent of `{DOC}-{n.m}` must be `{DOC}-{n}`.

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
| exec-summary | `ES` | MoSCoW | Why now, metrics, constraints, non-goals | Posture, vision, problem, what-must-be-true, viability verdict |
| mrd | `MRD` | Kano | Customer needs | Market overview, TAM/SAM/SOM (or internal cost-of-inaction), target segments (`**Primary:**` / `**Secondary:**`), competitors, trends, risks |
| brd | `BRD` | MoSCoW | Objectives, rules, dependencies | Stakeholders (buyer / user / approver in the section), business risks (impact × likelihood bullets) |
| prd | `PRD` | MoSCoW | Goals, stories, features, out-of-scope | Product overview, user personas (named in story bodies), release phasing |

Non-goals and PRD out-of-scope are `Won't` by definition. MRD segments state primary/secondary in the section (not a rank, not an id). MRD/BRD risks state impact × likelihood in the section. PRD `status` (e.g. `delivered`) is a manual leaf field — not derived from children.

### Emit: omit vs placeholder

Do not write keys that will never apply. Do not write `—` to mean “this field is not a thing.”

- **Omit** — empty by nature / inapplicable: containers have no `_moscow_` / `_kano_` (already `CONTAINER_RANK` if present). No `_status_` except on PRD leaves. No `_rationale_` until minted (never `_rationale_: —`). No method key on a heading that is not an item.
- **Placeholder `—`** — expected on this item, not yet decided: ranked leaf still `idea`/`draft` without a cut → `_moscow_: —` or `_kano_: —`. Drop the key once the real value is written, or replace `—` with Must/basic/etc.
- **Ready** — real rank required. `spec: ready` + missing method key or `—` is `DOR`, not an unranked item.

`—` = null for an applicable key not yet decided; omit inapplicable keys. `_parent_: —` on ES roots stays (graph null, not a rank).

### Per-level methods

Do not apply one ranking system to the whole cascade. No 1–5. No P0/P1/P2.

- **exec-summary — MoSCoW.** Posture, vision, problem, what-must-be-true, and viability verdict are **prose** (the anchor — no `ES-*` id). Metrics, constraints, non-goals, and why-now are Must/Should/Could/Won’t. Why: few items, board language, no implementation blast radius yet.
- **mrd — Kano on needs** (`basic` / `performance` / `delighter`). Why: market needs are about satisfaction-if-present vs dissatisfaction-if-absent; MoSCoW flattens delighters into Could.
- **brd — MoSCoW on objectives, rules, and dependencies.** Compliance/contractual rules are Must. Why: business-negotiation language for cutting scope.
- **prd — MoSCoW on goals, stories, and features.** Legend is posture-dependent ([project-posture.md](../project-posture.md)): Must is the cut *within this session's horizon*, not a hardcoded "MVP." Should/Could = later-in-horizon; Won't = never. No second rank (`horizon:`) on items. Optional `_status_:` on leaves (e.g. `delivered`) — manual, not derived. Mechanism-level detail routes to `tech.md` ([output-formats.md](../output-formats.md)).

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
| `spec == ready` | Real rank present (`—` does not count). Cross-doc parent must be `ready`. Same-doc container is exempt. |
| `deprecated` | Keep for history; revival requires a new id |
| Replacement | New item starts `spec: draft` (or `idea`). Old item `spec: deprecated` as soon as the successor exists |
| `idea` children | FAIL if an `idea` item has children |
| Depth | `shallow`: one-liners may be assumptions. `standard`/`deep`: blocking if a **ready** leaf is missing a real rank (`—` does not count) |

### Example mapping

- Login leaf solid, approved: `PRD-4.1 spec:ready _moscow_: Must`. Authz still fuzzy: `PRD-4.2 spec:draft`. Container `PRD-4 spec:draft`.
- Shipped feature: `PRD-4.1 spec:ready _status_: delivered` (manual marker).
- Replace a requirement: `PRD-4.1 spec:deprecated superseded_by:PRD-9`; `PRD-9 spec:draft supersedes:PRD-4.1` until user promotes `ready`.

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
_parent_: PRD-3 | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-014
```

Split segments on `\s+\|\s+(?=_[a-z][a-z0-9-]*_:)` so effect text may contain `|`. FAIL if a segment is not `_key_: value` or the key is unknown/duplicate.

| Keys (md surface) | Who | Internal / `items.json` |
|-------------------|-----|-------------------------|
| **Required (all items)** | `parent`, `kind`, `spec` | same |
| **Ranked leaves also** | `rationale` (`r-NNN`, minted in the ledger before compose prints it) | `rationale` |
| **PRD leaves also** | `status` (open string, e.g. `delivered`) | `status` |
| **Leaves, native method** | `moscow` \| `kano` | `moscow` \| `kano` |
| **Optional** | `supersedes`, `superseded-by`; `rationale` on containers | `supersedes`, `superseded_by` |

Canonical emit order: `parent, kind, spec, status, moscow, kano, rationale, supersedes, superseded-by`. Omit inapplicable keys. `--rewrite` must not inject method `—` when the source omitted the key. Emit only keys present on the item (plus required `parent`/`kind`/`spec` for a parseable header).

Unknown keys or missing required keys (`parent`, `kind`, `spec`) → validator FAIL. Body is the blockquote (AI-judged). `idea`/`draft` leaves may omit moscow/kano or emit `—`. `ready` leaves missing a **real** rank (`—` does not count) → `DOR`.

`_parent_: —` means graph null (ES roots). Native rank `—` means “applicable, not yet decided.”

JSON shape: [schemas/items.schema.json](../schemas/items.schema.json). Graph checks: `scripts/validate_planning.sh` (md-only; `--format yaml|json` is `UNSUPPORTED_FORMAT`).

**Code owns:** unique IDs, parent/supersede pointers, numbering density, kind invariant, required keys, status legality, doc/`items.json` drift, rationale id shape and resolution against `decision-ledger.yaml`.

**AI owns:** whether a leaf is actually atomic, whether MoSCoW is inflated, whether the shall is testable, whether a `flips_when` condition is well-chosen (never a script FAIL).

## Templates

### Container (any level)

```markdown
### PRD-3: Checkout
_parent_: BRD-2 | _kind_: container | _spec_: draft
```

### Leaf — MoSCoW (ES / BRD / PRD)

```markdown
#### PRD-3.1: Guest checkout
_parent_: PRD-3 | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-014

> As a guest, I can complete checkout without an account so that first purchase is not blocked.
```

### Leaf — Kano (MRD needs)

```markdown
#### MRD-2.1: Checkout without an account
_parent_: MRD-2 | _kind_: leaf | _spec_: ready | _kano_: basic | _rationale_: r-002
```

### Leaf — PRD with delivery status

```markdown
#### PRD-3.1: Guest checkout
_parent_: PRD-3 | _kind_: leaf | _spec_: ready | _moscow_: Must | _status_: delivered | _rationale_: r-014

> As a guest, I can complete checkout without an account.
```

## Item index

Each composed markdown file ends with an index. Column 4 is the level’s native field (`MoSCoW` / `Kano`). Containers show `—` in the method column because they have no rank, not because they are unranked leaves.

```markdown
## Item index

| ID | Parent | Spec | MoSCoW |
|----|--------|------|--------|
| PRD-3 | BRD-2 | draft | — |
| PRD-3.1 | PRD-3 | ready | Must |
```
