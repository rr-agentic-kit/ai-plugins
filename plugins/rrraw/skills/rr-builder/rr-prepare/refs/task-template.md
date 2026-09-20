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
builder_stage: null | prepare | plan | build | review | refactor | step_validate | task_validate
step_index: null | integer   # 0-based into Steps; omit when not in a task-step stage
step_plan_done: false | true   # current step_index only; reset on step advance
step_build_done: false | true
step_review_done: false | true
step_refactor_done: false | true
---
```

Cursor algorithm SoT: [../../refs/slice-pipeline.md](../../refs/slice-pipeline.md). Do not infer the four `step_*_done` flags from body prose.

## Body sections (required)

| Section | Content |
|---------|---------|
| **Goal** | One observable outcome for this capability atom |
| **Obligations** | Constitution cites + **cited tech ADRs** + delta obligations |
| **Read-first** | Paths/symbols/docs to open before coding |
| **Steps** | Ordered implementer steps (mechanism-bearing only). Plan stage writes sidecar `{NNNN}-{step}.plan.md` per [plan-schema.md](../../refs/plan-schema.md) (`step` = 1-based); after plan, add a one-line pointer on that item (`→ plan: \`{NNNN}-{step}.plan.md\``) — do **not** inline the five plan sections here |
| **Verify / done** | How to know the atom is done (product AC refs OK) |
| **Non-goals** | Explicit exclusions for this task |
| **Open risks** | Residual risks / `pending_tech` blockers |

Markdown + YAML only — no XML DSL.

## Id allocation

Mint via `docs/rr/tasks/registry.yaml` `next_id` (global monotonic). Ids start at **1** (never 0).

**Mechanical mint (stdout → value only):**

1. If registry exists: read `next_id`; allocate consecutive integers for this L1 batch; write back updated `next_id`. Emit only the allocated id list — do not paste the registry file into chat.
2. If registry missing: compute `max_id` as the maximum integer stem among existing `{NNNN}.md` under `docs/rr/tasks/` (shell/find that prints **one integer**, or `0` if none). Continue from `max_id+1`. Create registry with `next_id` set after allocation. **Do not** dump path listings into context for the LLM to filter.

Do not invent a second mint algorithm in phase contracts — this section is SoT.
