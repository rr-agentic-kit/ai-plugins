# constitution

**Audience: dual** — `refs/planning/doc-standards/dual-audience.md`  
**Owner:** Non-negotiable Plan constraints (engineering/product constitution).

**Path:** `docs/plan/constitution.md` when `arch_doc_mode: split`; otherwise a section of `architecture.md`.

**Load when:** Posture sets `arch_doc_mode`; standing layer authoring.

## Required sections

| Section | Content |
|---------|---------|
| **Human brief** | Decision/ask for reviewers — which non-negotiables matter now; feedback needed; no new IDs |
| **Non-negotiables** | Short, binding rules that do not change per feature |

## Content

Short, binding rules that do not change per feature — e.g. multi-tenant isolation, PII handling class, “no shared mutable DB across bounded contexts.”

| Do | Do not |
|----|--------|
| State non-negotiables as testable rules | Duplicate the full spine |
| Cite Discover constraints when inherited | Re-open market/viability |
| Keep short | Become a second PRD |

Write Human brief last from locked rules (or outline then refresh) — no invented claims. Persist only after `compose-prose` → `rr-humanize` when this is a standalone `.md`.

## Combined vs split

| `arch_doc_mode` | Placement |
|-----------------|-----------|
| `combined` | `## Constitution` inside `architecture.md` (Human brief may be the architecture brief covering both) |
| `split` | Standalone `constitution.md` next to architecture — own Human brief first |

## Done-when

- [ ] Human brief is reviewable without the full rule list
- Non-negotiables listed and distinct from feature deltas
- Mode matches posture
