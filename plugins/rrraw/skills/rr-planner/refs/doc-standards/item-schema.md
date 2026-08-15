# item-schema

**Owner:** Shared item identity, parent walk, atomic split, per-level priority methods, spec/build states, and parseable markdown. Numbering and status live here once — level standards keep section lists and done-when.

**Load when:** Discovering, composing, validating, or challenging any cascade doc.

Audience: compose agent + orchestrator. Humans read the markdown.

## Shared fields

Every numbered item has `id`, `parent`, `kind`, `spec`. Priority fields depend on the **document type** (not a per-item choice). `build` exists only on FRD leaves.

| Field | Where | Values |
|-------|-------|--------|
| `id` | all | `{DOC}-{n}` or `{DOC}-{n.m}` — see Numbering |
| `parent` | all | Immediate parent item ID, or `—` for ES roots |
| `kind` | all | `container` \| `leaf` |
| `spec` | all | `idea` \| `draft` \| `ready` \| `deprecated` |
| `build` | FRD leaves only | `none` \| `in_progress` \| `done` |
| `supersedes` / `superseded_by` | optional | Replacement pair (both ends or neither) |

Containers stay unmarked (no MoSCoW / Kano / triad). Index tables show the level’s native field.

## Numbering

- ID: `{DOC}-{n}[.{n}]` with prefixes `ES`, `MRD`, `BRD`, `PRD`, `FRD`.
- Continuous among **siblings** (`1, 2, 3` — no gaps at compose). Children of item 3 are `3.1`, `3.2`, … not new top-level numbers.
- Unique across the cascade because of the prefix (`PRD-3` ≠ `FRD-3`).
- Max depth **2** inside a document (`n.m`). Deeper means the parent is not a real grouping — split the parent into siblings.
- **Freeze on level completion.** First compose of a level mints dense IDs. After the cascade gate passes, later inserts append (next integer). Explicit re-compose of a frozen level rewrites parent refs in child docs via `item_registry` (so FRD does not point at a vanished `PRD-3`).

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

Prose overviews (product overview paragraph, system context, market overview, release-phasing narrative) stay unnumbered. Everything that is a claim, constraint, objective, need, rule, story, or requirement is an item.

| `kind` | Same-doc children | Body |
|--------|-------------------|------|
| `container` | ≥1 | Grouping title only — no shall / AC |
| `leaf` | none | Statement (+ Gherkin AC on FRD) |

**Kind invariant** is same-document nesting only. Cross-doc `parent:` is the cascade walk, not a child for `kind`. A PRD leaf may be the parent of FRD items.

An `idea` item must not have children (promote to `draft` first).

## Which sections are items

Declared per level. Native priority method is a property of the **document type**. Unranked leaves still emit the native key with value `—` (do not omit the key).

| Level | Prefix | Method | Rankable leaves | Unranked leaves (`—`) | Prose (unnumbered) |
|-------|--------|--------|-----------------|----------------------|--------------------|
| exec-summary | `ES` | MoSCoW | Why now, metrics, constraints, non-goals | Vision, problem | — |
| mrd | `MRD` | Kano | Customer needs | Segments, competitors, trends, risks | Market overview |
| brd | `BRD` | MoSCoW | Objectives, rules, dependencies | Stakeholders, risks | — |
| prd | `PRD` | MoSCoW | Goals, stories, features | Personas | Product overview, release phasing |
| frd | `FRD` | triad | All leaves | — | System overview |

Non-goals and PRD out-of-scope are `Won't` by definition. MRD segments state primary/secondary in the body (not a rank). MRD/BRD risks state impact × likelihood in the body.

### Per-level methods

Do not apply one ranking system to the whole cascade. No 1–5. No P0/P1/P2.

- **exec-summary — MoSCoW.** Vision and problem are unranked (they are the anchor). Metrics, constraints, and non-goals are Must/Should/Could/Won’t. Why: few items, board language, no implementation blast radius yet.
- **mrd — Kano on needs** (`basic` / `performance` / `delighter`). Why: market needs are about satisfaction-if-present vs dissatisfaction-if-absent; MoSCoW flattens delighters into Could.
- **brd — MoSCoW on objectives, rules, and dependencies.** Compliance/contractual rules are Must. Why: business-negotiation language for cutting scope.
- **prd — MoSCoW on goals, stories, and features.** Must = MVP, Should = v1, Could = later, Won’t = out of scope (aligns with release phasing). Do not add `if_wrong` here — there is no design yet to be wrong.
- **frd — consequence triad + derived class.** First layer that must tell an implementer *how carefully* to build. Do not copy MoSCoW onto FRD items.

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
| `spec == ready` | Required keys for that level present. Cross-doc parent must be `ready`. Same-doc container is exempt. |
| `deprecated` | `build` cannot move to `in_progress`; existing `in_progress`/`done` is a **warning** (code still in tree, spec withdrawn) |
| Replacement | New item starts `spec: draft` (or `idea`), `build: none`. Old item `spec: deprecated` as soon as the successor exists |
| `idea` children | FAIL if an `idea` item has children |
| Depth | `shallow`: method field required on leaves still; one-liners may be assumptions. `standard`/`deep`: blocking if method fields missing on a leaf |

### Example mapping

- Login leaf solid, already coding: `FRD-4.1 spec:ready build:in_progress`. Authz still fuzzy: `FRD-4.2 spec:draft build:none`. Container `FRD-4 spec:draft`.
- Replace a requirement: `FRD-4.1 spec:deprecated superseded_by:FRD-9`; `FRD-9 spec:draft supersedes:FRD-4.1 build:none` until triad+AC exist and user promotes `ready`.

## Canonical markdown (closed vocabulary)

Working surface is markdown. Validation target is structured. Compose always writes both `*.md` and `items.json`.

Heading (regex, not an LLM):

```
^(#{2,4}) (ES|MRD|BRD|PRD|FRD)-(\d+(?:\.\d+)?): (.+)$
```

Metadata lines immediately under the heading, until a blank line:

```
^- \*\*(.+?):\*\* (.+)$
```

| Keys | Who |
|------|-----|
| **Required (all items)** | `Parent`, `Kind`, `Spec` |
| **FRD leaves also** | `Build` |
| **Leaves, native method** | `MoSCoW` \| `Kano` \| `If present` / `If absent` / `If wrong` / `Class` |
| **Optional** | `Supersedes`, `Superseded-by` |

Unknown keys or missing required keys → validator FAIL. Body after the blank line is free markdown (AI-judged).

`Parent: —` and native rank `—` mean null / unranked. Triad lines: `<magnitude> — <effect>` (em dash preferred).

JSON shape: [schemas/items.schema.json](../schemas/items.schema.json). Graph checks: `plugins/rrraw/scripts/validate_planning.py`.

**Code owns:** unique IDs, parent/supersede pointers, numbering density, kind invariant, required keys, status legality, md/json drift.

**AI owns:** whether a leaf is actually atomic, whether MoSCoW is inflated, whether `if_wrong` is a real blast radius, whether the shall is testable.

## Templates

### Container (any level)

```markdown
### PRD-3: Checkout
- **Parent:** BRD-2
- **Kind:** container
- **Spec:** draft
```

### Leaf — MoSCoW (ES / BRD / PRD)

```markdown
#### PRD-3.1: Guest checkout
- **Parent:** PRD-3
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** Must

As a guest, I can complete checkout without an account so that first purchase is not blocked by registration.
```

### Leaf — Kano (MRD needs)

```markdown
#### MRD-2.1: Checkout without an account
- **Parent:** MRD-2
- **Kind:** leaf
- **Spec:** ready
- **Kano:** basic
```

### Leaf — triad (FRD)

```markdown
#### FRD-4.1: Guest checkout without account
- **Parent:** PRD-3.1
- **Kind:** leaf
- **Spec:** ready
- **Build:** in_progress
- **If present:** high — Unlocks self-serve conversion without an account
- **If absent:** high — PLG motion blocked (BRD-2); assisted sales stays the path
- **If wrong:** critical — Bad tax/entitlements → billing disputes
- **Class:** must-correct

The system shall allow checkout without an account.

**Acceptance criteria:**
- Given [context], When [action], Then [outcome]
- Given [error context], When [invalid action], Then [error behavior]
```

## Item index

Each composed markdown file ends with an index. Column 4 is the level’s native field (`MoSCoW` / `Kano` / `Class`). Containers and unranked leaves show `—`.

```markdown
## Item index

| ID | Parent | Spec | MoSCoW |
|----|--------|------|--------|
| PRD-3 | BRD-2 | draft | — |
| PRD-3.1 | PRD-3 | ready | Must |
```
