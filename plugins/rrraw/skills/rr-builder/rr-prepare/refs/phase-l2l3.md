# Phase L2+L3 — agent-shaped contract

**Audience:** Parent session today; future Task agent without rewriting this contract.

## Inject (caller → phase)

| Field | Required |
|-------|----------|
| Validated `task-summary.md` path + `slice_id` | yes |
| `posture` + `pending_tech` | yes |
| Next task id to detail (L2) or `mode: l3` | yes |
| Refs to load | `task-template.md`, `compatibility-gate.md`, `sequencing.md`, `tech-decisions.md`; for L3 also `pr-division.md` |

## Load (phase must Read)

1. Summary + kernel pins for the active task’s `requirement_ids`
2. Cited ADRs / code paths for mechanism
3. Injected refs

## L2 work (one task)

1. Research code/docs/web as needed for posture.
2. Force-mint ADR if blocked by `pending_tech` and irreversible.
3. Write `docs/rr/tasks/{slice_id}/{NNNN}.md`.
4. Run compatibility gate — FAIL → do not mark `detailed`.
5. Mark summary row `detailed`; re-check sequencing.

Default: return after **one** task so parent can validate.

## L3 work (once, after all detailed)

1. Apply PR division heuristics.
2. Set `pr_group` on tasks + summary PR map.
3. Set `prepare_status: complete`.

## Output

| Mode | Artifacts |
|------|-----------|
| L2 | `{NNNN}.md` + summary row update |
| L3 | summary PR map + frontmatter `pr_group` + `prepare_status: complete` |

## Stop

L2: return after each task (or batch only if parent requested). L3: prepare complete — **do not** invoke **rr-coder**.
