# architecture (standing spine)

**Audience: dual** — `refs/planning/doc-standards/dual-audience.md`  
**Owner:** Standing architecture spine standard — invariants only.

**Path:** `docs/rr/{track}/plan/architecture.md`  
**Load when:** Plan `standing` todo; same-sitting Effort; slice freeze pins.

**Does not:** Restate full stack/tree as the spine. Stack dump may seed; spine is invariants. Product AC stays on PRD.

## Spine test

Record only decisions that would **diverge if two units built independently**.

| Marker | Meaning |
|--------|---------|
| **Binds** | Shared obligation every implementation must honor |
| **Prevents** | Forbidden divergence |
| **Rule** | Named policy (naming, auth boundary, tenancy, …) |

Also allow short sections: **Deferred**, **Inherited** (from Discover constraints / business-case).

## Required sections

| Section | Content |
|---------|---------|
| **Human brief** | Spine purpose + binds that matter for review; what feedback is needed — plain language, no new IDs |
| **Purpose** | One paragraph — what this spine protects |
| **Invariants** | `Binds` / `Prevents` / `Rule` bullets or ADR-lite entries (`skills/rr-planner/refs/adr-lite.md`) |
| **Deferred** | Explicitly postponed decisions |
| **Inherited** | Constraints pulled from frozen Discover (cite ids) |
| **Seed (optional)** | Minimal stack notes — labeled seed, not binding spine |

When `arch_doc_mode: combined`, include a **Constitution** subsection ([constitution.md](constitution.md)). When `split`, constitution is a separate file.

Write Human brief last from locked invariants (or outline then refresh) — no invented binds. Persist only after `compose-prose` → `rr-humanize`.

## Rev / draft

Frontmatter may carry `doc_rev: "?"` while draft. Slice freeze may pin `architecture_rev: draft`. Accepted invariants follow supersede-only rules.

## Done-when

- [ ] Human brief is reviewable without decoding the full invariant list
- Invariants use Bind/Prevent/Rule language
- No full design dump posing as spine
- Feature work references this file instead of copying it
