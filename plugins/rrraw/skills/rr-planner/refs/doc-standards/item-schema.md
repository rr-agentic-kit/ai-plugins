# item-schema

**Owner:** Shared item identity, parent walk, atomic split, per-level priority methods, spec/build states, and parseable markdown. Numbering and status live here once — level standards keep section lists and done-when.

**Load when:** Discovering, composing, validating, or challenging any cascade doc.

Audience: compose agent + orchestrator. Working surface is markdown. Validation target is structured (`items.json`).

## Shared fields

Every numbered item has `id`, `parent`, `kind`, `spec`. Priority fields depend on the **document type** (not a per-item choice). `build` exists only on FRD leaves.

| Field | Where | Values |
|-------|-------|--------|
| `id` | all | `{DOC}-{n}` or `{DOC}-{n.m}` — see Numbering |
| `parent` | all | Immediate parent item ID, or `—` for ES roots |
| `kind` | all | `container` \| `leaf` |
| `spec` | all | `idea` \| `draft` \| `ready` \| `deprecated` |
| `build` | FRD leaves only | `none` \| `in_progress` \| `done` |
| `rationale` | ranked leaves | `r-\d{3,}` pointer into [decision-ledger.md](../decision-ledger.md). Optional on containers. Required once the leaf has a real rank value. Never emit `_rationale_: —`. |
| `supersedes` / `superseded-by` | optional | Replacement pair (both ends or neither). JSON field remains `superseded_by`. |

Containers stay unmarked (no MoSCoW / Kano / triad). Index tables show the level’s native field.

## Numbering

- ID: `{DOC}-{n}[.{n}]` with prefixes `ES`, `MRD`, `BRD`, `PRD`, `FRD`.
- **Mint `{DOC}-n` only for what the level ranks** (plus containers that group ranked leaves). Unranked narrative, already-labeled partitions, and context lists stay unnumbered prose. Numbering exists to (1) rank, (2) nest ranked children, (3) parent-walk. If none apply, the heading is prose. Do not invent semantic ids (`exec-vision`, `mrd-primary`, `prd-persona`).
- Continuous among **siblings** (`1, 2, 3` — no gaps at compose). Children of item 3 are `3.1`, `3.2`, … not new top-level numbers.
- Unique across the cascade because of the prefix (`PRD-3` ≠ `FRD-3`).
- Max depth **2** inside a document (`n.m`). Deeper means the parent is not a real grouping — split the parent into siblings.
- **Freeze / remap** (when IDs freeze, append-only inserts, re-compose rewrite): [cascade.md](../cascade.md). This ref owns ID shape, sibling density, and max depth.

Rejected: one global `1…N` across all five docs. Rejected: semantic names (`exec-vision`) — not continuous, do not nest.

## Parent pointer

Single field `parent:` = **immediate** parent item ID.

| Case | Value |
|------|-------|
| ES roots | `—` |
| Nested child (same doc) | `PRD-3` |
| Cross-doc | `BRD-2` (previous cascade level only) |

Full chain is a walk: `FRD-4.1 → FRD-4 → PRD-3.1 → PRD-3 → BRD-2 → … → ES-1`. Success-criteria validates the walk. Docs do **not** repeat the whole chain on every item.

Cross-doc parent must be the previous cascade level (no skips). Same-doc parent of `{DOC}-{n.m}` must be `{DOC}-{n}`.

## Atomic split

**One leaf = one testable statement.** A container has children and no `shall` of its own. A leaf has body (+ AC on FRD) and no children. Never both.

Split when a fact has multiple independent shalls, multiple actors, or a list of distinct outcomes. Example: “5 requirements for checkout” → `PRD-3` container + `PRD-3.1`…`PRD-3.5` leaves.

Prose overviews and unranked context (vision, posture, segments, personas, stakeholders, risks, sizing) stay unnumbered. Ranked claims — constraints, objectives, needs, rules, stories, features, requirements — are items. After compose, **no level has unranked leaves.** `—` is not a rank class. It is a placeholder for a field that belongs on this item but is not decided yet.

| `kind` | Same-doc children | Body |
|--------|-------------------|------|
| `container` | ≥1 | Grouping title only — no shall / AC |
| `leaf` | none | Statement (+ Gherkin AC on FRD) |

**Kind invariant** is same-document nesting only. Cross-doc `parent:` is the cascade walk, not a child for `kind`. A PRD leaf may be the parent of FRD items.

An `idea` item must not have children (promote to `draft` first).

## Which sections are items

Declared per level. Native priority method is a property of the **document type**.

| Level | Prefix | Method | Rankable leaves | Prose (unnumbered) |
|-------|--------|--------|-----------------|--------------------|
| exec-summary | `ES` | MoSCoW | Why now, metrics, constraints, non-goals | Posture, vision, problem, what-must-be-true, viability verdict |
| mrd | `MRD` | Kano | Customer needs | Market overview, TAM/SAM/SOM (or internal cost-of-inaction), target segments (`**Primary:**` / `**Secondary:**`), competitors, trends, risks |
| brd | `BRD` | MoSCoW | Objectives, rules, dependencies | Stakeholders (buyer / user / approver in the section), business risks (impact × likelihood bullets) |
| prd | `PRD` | MoSCoW | Goals, stories, features, out-of-scope | Product overview, user personas (named in story bodies), release phasing |
| frd | `FRD` | triad | All leaves | System overview |

Non-goals and PRD out-of-scope are `Won't` by definition. MRD segments state primary/secondary in the section (not a rank, not an id). MRD/BRD risks state impact × likelihood in the section.

### Emit: omit vs placeholder

Do not write keys that will never apply. Do not write `—` to mean “this field is not a thing.”

- **Omit** — empty by nature / inapplicable: containers have no `_moscow_` / `_kano_` / triad (already `CONTAINER_RANK` if present). Non-FRD has no `_build_`. No `_rationale_` until minted (never `_rationale_: —`). No method key on a heading that is not an item.
- **Placeholder `—`** — expected on this item, not yet decided: ranked leaf still `idea`/`draft` without a cut → `_moscow_: —` or `_kano_: —`. Drop the key once the real value is written, or replace `—` with Must/basic/etc.
- **Ready** — real rank required. `spec: ready` + missing method key or `—` is `DOR`, not an unranked item.

`—` = null for an applicable key not yet decided; omit inapplicable keys. `_parent_: —` on ES roots stays (graph null, not a rank).

### Per-level methods

Do not apply one ranking system to the whole cascade. No 1–5. No P0/P1/P2.

- **exec-summary — MoSCoW.** Posture, vision, problem, what-must-be-true, and viability verdict are **prose** (the anchor — no `ES-*` id). Metrics, constraints, non-goals, and why-now are Must/Should/Could/Won’t. Why: few items, board language, no implementation blast radius yet.
- **mrd — Kano on needs** (`basic` / `performance` / `delighter`). Why: market needs are about satisfaction-if-present vs dissatisfaction-if-absent; MoSCoW flattens delighters into Could.
- **brd — MoSCoW on objectives, rules, and dependencies.** Compliance/contractual rules are Must. Why: business-negotiation language for cutting scope.
- **prd — MoSCoW on goals, stories, and features.** Legend is posture-dependent ([project-posture.md](../project-posture.md)): Must is the cut *within this session's horizon*, not a hardcoded "MVP." Should/Could = later-in-horizon; Won't = never. No second rank (`horizon:`) on items. Do not add `if_wrong` here — there is no design yet to be wrong.
- **frd — consequence triad + derived class.** First layer that must tell an implementer *how carefully* to build. Do not copy MoSCoW onto FRD items. Triad inheritance is unchanged (Must → high absence, Should → moderate, Could → low); only the human PRD legend changes.

### FRD consequence triad (leaves only)

Each axis: magnitude `critical | high | moderate | low` plus one-line effect.

| Axis | Meaning |
|------|---------|
| **If present** | Value unlocked when done right |
| **If absent** | What breaks or stalls if skipped |
| **If wrong** | Blast radius of a defective implementation |

**Inheritance, not duplication.** An FRD leaf may default `if_absent` magnitude from the parent PRD MoSCoW (Must → high, Should → moderate, Could → low, Won’t → do not compose a child). It must still fill `if_wrong` — that is new information at this layer.

Derived **class** is an exclusive partition (first match). Treat `critical` as high:

| Class | When | Build implication |
|-------|------|-------------------|
| `must-correct` | high absence **and** high wrongness | MVP + heavy AC |
| `must-present` | high absence, not high wrongness | MVP, happy-path enough |
| `protect` | high wrongness, not high absence | Defer, or isolate + tests + rollback if built |
| `leverage` | high presence, low absence, low wrongness | Later, sequence by payoff |
| `optional` | else | Cut freely |

`high` on an axis means magnitude `critical` or `high`. Validator FAILs if `Class` disagrees with this table.

## Spec and build (two axes)

One status list mixing “is the spec agreed” with “is it in the product” cannot say: this leaf is coding, sibling still in draft, replacement must not be built.

### Axis 1 — `spec` (all items, all docs)

`idea` → `draft` → `ready` → `deprecated`

| State | Meaning | Implement? |
|-------|---------|------------|
| `idea` | Inbox. Captured, existence **not** committed, **not** being authored. Parked. | no |
| `draft` | Spec WIP. Existence committed; fields may be incomplete; writing/splitting/clarifying. | no |
| `ready` | DoR met **and** explicitly approved. | FRD leaves may take `build != none` |
| `deprecated` | Do not implement; keep for history. | no |

Skip `draft` when the item arrives complete: `idea → ready` is legal. Do not require a fake WIP hop.

Containers have `spec` only. A container may stay `draft` while one child is `ready`. **Only leaves are implementable.**

Legal transitions: `idea → draft|ready|deprecated`; `draft → ready|idea|deprecated`; `ready → draft` (reopen) `| deprecated`; `deprecated` terminal (revive = new id).

Discovery defaults new items to `idea`. Moving to `draft` means “we are specifying this now.” Compose does **not** auto-promote to `ready` because fields exist — promotion is a user/gate action.

Dropped (do not encode): extra `discussion` / `review` / `analyzed` states; implementation WIP on `spec`.

### Axis 2 — `build` (FRD leaves only)

`none` → `in_progress` → `done`

Omit `build` on ES/MRD/BRD/PRD and on all containers. PRD “delivered” is **derived**: Must FRD children of that story are `done`. Do not store it on PRD.

### DoR / DoD-lite (code gates)

| Rule | Effect |
|------|--------|
| `build != none` | `kind == leaf` AND doc is FRD AND `spec == ready` |
| `spec == ready` | Real rank present (`—` does not count). Cross-doc parent must be `ready`. Same-doc container is exempt. |
| `deprecated` | `build` cannot move to `in_progress`; existing `in_progress`/`done` is a **warning** (code still in tree, spec withdrawn) |
| Replacement | New item starts `spec: draft` (or `idea`), `build: none`. Old item `spec: deprecated` as soon as the successor exists |
| `idea` children | FAIL if an `idea` item has children |
| Depth | `shallow`: one-liners may be assumptions. `standard`/`deep`: blocking if a **ready** leaf is missing a real rank (`—` does not count) |

### Example mapping

- Login leaf solid, already coding: `FRD-4.1 spec:ready build:in_progress`. Authz still fuzzy: `FRD-4.2 spec:draft build:none`. Container `FRD-4 spec:draft`.
- Replace a requirement: `FRD-4.1 spec:deprecated superseded_by:FRD-9`; `FRD-9 spec:draft supersedes:FRD-4.1 build:none` until triad+AC exist and user promotes `ready`.

## Canonical item surface (closed vocabulary)

Working surface is markdown. Validation target is structured. Compose writes `{level}.md` and merges `items.json`. Item records live on disk, not in the Task return. Cascade `{stem}.yaml` and list-meta (`- **Key:**`) are stale — `validate_planning.py --rewrite` migrates them.

Parser is regex, not an LLM. Three-line grammar:

1. Heading = id + title
2. Next non-empty line = closed metadata (`_key_:`)
3. Following `^> ?` lines = body; anything else before the next heading is prose or `STALE_FORMAT`. Leaf body without `>` is `BODY_NOT_BLOCKQUOTE`. Containers have no `>` body.

Heading:

```
^(#{2,4}) (ES|MRD|BRD|PRD|FRD)-(\d+(?:\.\d+)?): (.+)$
```

Metadata — one line immediately under the heading. Keys are hyphenated (`_if-present_`, `_superseded-by_`), not snake_case, so wrapping `_key_:` renders as one italic span.

```
_parent_: PRD-3 | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-014
```

Split segments on `\s+\|\s+(?=_[a-z][a-z0-9-]*_:)` so triad effect text may contain `|`. FAIL if a segment is not `_key_: value` or the key is unknown/duplicate.

| Keys (md surface) | Who | Internal / `items.json` |
|-------------------|-----|-------------------------|
| **Required (all items)** | `parent`, `kind`, `spec` | same |
| **Ranked leaves also** | `rationale` (`r-NNN`, minted in the ledger before compose prints it) | `rationale` |
| **FRD leaves also** | `build` | `build` |
| **Leaves, native method** | `moscow` \| `kano` \| `if-present` / `if-absent` / `if-wrong` / `class` | `moscow` \| `kano` \| `triad.if_present` / `if_absent` / `if_wrong` / `class` |
| **Optional** | `supersedes`, `superseded-by`; `rationale` on containers | `supersedes`, `superseded_by` |

Canonical emit order: `parent, kind, spec, build, moscow, kano, if-present, if-absent, if-wrong, class, rationale, supersedes, superseded-by`. Omit inapplicable keys. `--rewrite` must not inject method `—` when the source omitted the key. Emit only keys present on the item (plus required `parent`/`kind`/`spec` for a parseable header).

Unknown keys or missing required keys (`parent`, `kind`, `spec`) → validator FAIL. Body is the blockquote (AI-judged). `idea`/`draft` leaves may omit moscow/kano or emit `—`. `ready` leaves missing a **real** rank (`—` does not count) → `DOR`.

`_parent_: —` means graph null (ES roots). Native rank `—` means “applicable, not yet decided.” Triad values: `<magnitude> — <effect>` (em dash preferred).

JSON shape: [schemas/items.schema.json](../schemas/items.schema.json). Graph checks: `scripts/validate_planning.py` (md-only; `--format yaml|json` is `UNSUPPORTED_FORMAT`).

**Code owns:** unique IDs, parent/supersede pointers, numbering density, kind invariant, required keys, status legality, doc/`items.json` drift, rationale id shape and resolution against `decision-ledger.yaml`.

**AI owns:** whether a leaf is actually atomic, whether MoSCoW is inflated, whether `if_wrong` is a real blast radius, whether the shall is testable, whether a `flips_when` condition is well-chosen (never a script FAIL).

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

### Leaf — triad (FRD)

```markdown
#### FRD-4.1: Guest checkout without account
_parent_: PRD-3.1 | _kind_: leaf | _spec_: ready | _build_: in_progress | _if-present_: high — Unlocks self-serve conversion without an account | _if-absent_: high — PLG motion blocked (BRD-2); assisted sales stays the path | _if-wrong_: critical — Bad tax/entitlements → billing disputes | _class_: must-correct | _rationale_: r-014

> The system shall allow checkout without an account.
>
> **Acceptance criteria:**
> - Given [context], When [action], Then [outcome]
> - Given [error context], When [invalid action], Then [error behavior]
```

## Item index

Each composed markdown file ends with an index. Column 4 is the level’s native field (`MoSCoW` / `Kano` / `Class`). Containers show `—` in the method column because they have no rank, not because they are unranked leaves.

```markdown
## Item index

| ID | Parent | Spec | MoSCoW |
|----|--------|------|--------|
| PRD-3 | BRD-2 | draft | — |
| PRD-3.1 | PRD-3 | ready | Must |
```
