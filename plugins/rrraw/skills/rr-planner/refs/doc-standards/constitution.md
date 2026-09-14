# constitution (standing law)

**Audience: dual** — `refs/planning/doc-standards/dual-audience.md`  
**Owner:** Standing always-load Plan law — human brief + invariant INDEX (Bind/Prevent/Rule one-liners) + Deferred/Inherited.

**Path:** `docs/rr/{track}/plan/constitution.md`  
**Load when:** Always for Plan body / dual-lens / research / challenge supporting context. Posture prefers `arch_doc_mode: constitution-primary`.

**Does not:** Hold full decision-lite bodies when sharded under `constitution/invariants/`. Does not own feature mechanism (→ `deltas/`). Does not own stack/C4/tech ADR catalogs (→ `architecture.md`).

## Spine test (INDEX)

Record only decisions that would **diverge if two units built independently**, or that set a **global interaction / design-system baseline** every UI feature must honor — as **one-liners** in the INDEX.

| Marker | Meaning |
|--------|---------|
| **Binds** | Shared obligation every implementation must honor (tech or UX baseline) |
| **Prevents** | Forbidden divergence |
| **Rule** | Named policy (naming, auth boundary, tenancy, interaction pattern, …) |

Also: **Deferred**, **Inherited** (from Discover constraints / business-case).

Global UX baseline enters the INDEX **only** via Bind/Prevent/Rule. Feature-local UX-shape lives in `deltas/<feature-id>.md`.

## Required sections

| Section | Content |
|---------|---------|
| **Human brief** | Which non-negotiables matter now; feedback needed — plain language, no new IDs |
| **Invariant INDEX** | Bind/Prevent/Rule one-liners (+ Deferred / Inherited). Optional pointers to `constitution/invariants/*.md` decision-lite bodies |
| **Non-negotiables** | Short binding rules that do not change per feature (may overlap INDEX; keep terse) |

| Do | Do not |
|----|--------|
| Keep INDEX scannable (always-load) | Dump full ADR/decision bodies into the always-load file |
| Cite Discover constraints when inherited | Re-open market/viability |
| Point to on-demand shards / tech ADRs | Become a second PRD or stack dump |

Write Human brief last from locked rules — no invented claims. Persist only after `compose-prose` → `rr-humanize`.

## `arch_doc_mode`

| Mode | Placement |
|------|-----------|
| `constitution-primary` (**prefer**) | Standalone `constitution.md` always; `architecture.md` = tech ADRs only when needed |
| `legacy-combined` (transition) | Constitution still embedded in a fat `architecture.md` — migrate via `--optimize`; do not mint new combined blobs |

## Rev / draft

Frontmatter may carry `doc_rev: "?"` while draft. Slice freeze may pin `constitution_rev` (prefer) and dual-read `architecture_rev` during transition. **Draft ≠ missing:** freeze still requires Decision + Effort drivers for selected capabilities.

## Done-when

- [ ] Human brief reviewable without decoding the full INDEX
- INDEX uses Bind/Prevent/Rule one-liners
- No product UX catalog or stack dump posing as standing law
- Feature work references this file instead of copying it
