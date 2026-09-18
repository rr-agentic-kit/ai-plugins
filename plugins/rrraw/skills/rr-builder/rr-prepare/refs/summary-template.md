# Task summary template

**Path:** `docs/rr/tasks/{slice_id}/task-summary.md`

## Frontmatter

```yaml
---
slice_id: slice-001
track: "0.1"
kernel_path: docs/rr/0.1/plan/execute-slice.yaml
posture: greenfield
prepare_status: l1 | l2 | complete
pending_tech: []
doc_drift: null
---
```

## Ordered task table

| id | title | depends_on | requirement_ids | status | pr_group | outcome |
|----|-------|------------|-----------------|--------|----------|---------|
| 1 | … | [] | […] | outlined \| detailed | null \| g1 | one-line |

Optional column / note: `doc_drift` when brownfield posture marked drift.

## Pending tech

Mirror [tech-decisions.md](tech-decisions.md) inventory until resolved.

## PR map (L3)

| pr_group | task_ids | rationale |
|----------|----------|-----------|
| g1 | [1, 2] | … |

## Registry pointer

Global ids SoT: `docs/rr/tasks/registry.yaml` (`next_id` + optional index). This summary does not restart ids per slice.
