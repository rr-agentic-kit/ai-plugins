# constitution

**Owner:** Non-negotiable Plan constraints (engineering/product constitution).

**Path:** `docs/plan/constitution.md` when `arch_doc_mode: split`; otherwise a section of `architecture.md`.

**Load when:** Posture sets `arch_doc_mode`; standing layer authoring.

## Content

Short, binding rules that do not change per feature — e.g. multi-tenant isolation, PII handling class, “no shared mutable DB across bounded contexts.”

| Do | Do not |
|----|--------|
| State non-negotiables as testable rules | Duplicate the full spine |
| Cite Discover constraints when inherited | Re-open market/viability |
| Keep short | Become a second PRD |

## Combined vs split

| `arch_doc_mode` | Placement |
|-----------------|-----------|
| `combined` | `## Constitution` inside `architecture.md` |
| `split` | Standalone `constitution.md` next to architecture |

## Done-when

- Non-negotiables listed and distinct from feature deltas
- Mode matches posture
