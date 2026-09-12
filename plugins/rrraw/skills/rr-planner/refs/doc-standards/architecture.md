# architecture (standing spine)

**Audience: dual** — `refs/planning/doc-standards/dual-audience.md`  
**Owner:** Standing architecture spine standard — invariants only (tech + global UX baseline when Bind/Prevent would diverge).

**Path:** `docs/rr/{track}/plan/architecture.md`  
**Load when:** Plan `standing` todo; same-sitting Effort; slice freeze pins.

**Does not:** Restate full stack/tree as the spine. Stack dump may seed; spine is invariants. Product AC stays on PRD. Does not dump component libraries as binding spine. Feature-local UX-shape lives in deltas.

## Spine test

Record only decisions that would **diverge if two units built independently**, or that set a **global interaction / design-system baseline** every UI feature must honor.

| Marker | Meaning |
|--------|---------|
| **Binds** | Shared obligation every implementation must honor (tech or UX baseline) |
| **Prevents** | Forbidden divergence |
| **Rule** | Named policy (naming, auth boundary, tenancy, interaction pattern, …) |

Also allow short sections: **Deferred**, **Inherited** (from Discover constraints / business-case).

Global UX baseline (design-system / interaction-pattern) enters the spine **only** via Bind/Prevent/Rule (or a labeled Seed that is explicitly binding). Do not park feature-local screens or cost-relevant states here — those belong in `deltas/<feature-id>.md` UX-shape.

## Required sections

| Section | Content |
|---------|---------|
| **Human brief** | Spine purpose + binds that matter for review; what feedback is needed — plain language, no new IDs |
| **Purpose** | One paragraph — what this spine protects |
| **Invariants** | `Binds` / `Prevents` / `Rule` bullets or ADR-lite entries (`skills/rr-planner/refs/adr-lite.md`) |
| **Deferred** | Explicitly postponed decisions |
| **Inherited** | Constraints pulled from frozen Discover (cite ids) |
| **Seed (optional)** | Minimal stack / UX-baseline notes — labeled seed; binding only when marked as Bind/Prevent/Rule |

When `arch_doc_mode: combined`, include a **Constitution** subsection ([constitution.md](constitution.md)). When `split`, constitution is a separate file.

Write Human brief last from locked invariants (or outline then refresh) — no invented binds. Persist only after `compose-prose` → `rr-humanize`.

## Rev / draft

Frontmatter may carry `doc_rev: "?"` while draft. Slice freeze may pin `architecture_rev: draft`. **Draft ≠ missing:** freeze still requires Decision + Effort drivers for selected capabilities (draft rev OK). Accepted invariants follow supersede-only rules.

## Done-when

- [ ] Human brief is reviewable without decoding the full invariant list
- Invariants use Bind/Prevent/Rule language
- Global UX baseline only when Bind/Prevent would diverge — not a component catalog
- No full design dump posing as spine
- Feature work references this file instead of copying it
