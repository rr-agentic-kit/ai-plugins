# Phase L1 — agent-shaped contract

**Audience:** Parent session today; future Task agent without rewriting this contract.

## Inject (caller → phase)

| Field | Required |
|-------|----------|
| `kernel_path`, `slice_id`, `track`, `posture` | yes |
| Pin excerpts (requirement ids, delta paths list, constitution INDEX cites) | yes |
| `pending_tech` snapshot | yes (may be empty) |
| Refs to load | `task-grain.md`, `sequencing.md`, `summary-template.md`, `tech-decisions.md` (read-only) |

## Load (phase must Read)

1. Kernel + listed deltas (paths from inject)
2. Constitution INDEX
3. `docs/rr/tasks/registry.yaml` (create with `next_id: 1` if absent)
4. Injected refs above

## Work

1. Decompose Capabilities into ordered capability atoms (grain rubric).
2. Allocate global ids; build DAG `depends_on`.
3. Write `docs/rr/tasks/{slice_id}/task-summary.md`.
4. Update `pending_tech` topics blocked by L1 order if any.

## Output

| Artifact | Required |
|----------|----------|
| `task-summary.md` with outlined rows | yes |
| Updated `registry.yaml` `next_id` | yes if ids minted |
| Forced `ADR-n` only if L1 order invents mechanism otherwise | optional |

## Stop

Return to parent. Parent **validates L1** with human/session before L2. Do not write `{NNNN}.md` in this phase.
