# Task file template (`{NNNN}.md`)

**Path:** `docs/rr/tasks/{slice_id}/{NNNN}.md` — zero-padded four-digit filename; frontmatter `id` is the integer.

## Frontmatter

```yaml
---
id: 1
slice_id: slice-001
track: "0.1"
depends_on: []
requirement_ids: [PRD-3.1]
files_likely: []
pr_group: null
adr_refs: []
status: detailed
---
```

## Body sections (required)

| Section | Content |
|---------|---------|
| **Goal** | One observable outcome for this capability atom |
| **Obligations** | Constitution cites + **cited tech ADRs** + delta obligations |
| **Read-first** | Paths/symbols/docs to open before coding |
| **Steps** | Ordered implementer steps (mechanism-bearing) |
| **Verify / done** | How to know the atom is done (product AC refs OK) |
| **Non-goals** | Explicit exclusions for this task |
| **Open risks** | Residual risks / `pending_tech` blockers |

Markdown + YAML only — no XML DSL.

## Id allocation

Mint via `docs/rr/tasks/registry.yaml` `next_id` (global monotonic). On mint, if registry missing: scan max existing `{NNNN}.md` under `docs/rr/tasks/` and continue. Ids start at **1** (never 0).
