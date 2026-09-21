# Feature mode (ad-hoc task mint + run)

**Audience:** `rr-builder` when `payload.mode: feature`. SoT for detect → branch ensure → mint → task-scoped pipeline → hard stop at task-validate. Reuses prepare mint templates + [slice-pipeline.md](slice-pipeline.md) — **do not** fork a second stage matrix.

**Not:** plan-stage [feature-branch.md](feature-branch.md) (per-step `feat/{NNNN}-{step}-*`); product Feature delta / rr-planner Plan; full-slice `--slice`.

## Flow

```
detect project_kind
  → AskQuestion origin if branch not task-dedicated
  → mint task (rr vs .ai)
  → set cursor on new task
  → run slice-pipeline with scope=task until task-validate PASS
  → stop (no slice-validate / delivered)
```

## Detect (`project_kind`)

| Signal | `project_kind` |
|--------|----------------|
| `docs/rr/` present (prefer `docs/rr/rrr-status.yaml` when present) | `rr` |
| else | `non_rr` |

**Never** create `docs/rr/` under `--feature`.

### Artifact root

| `project_kind` | `artifact_root` | Notes |
|----------------|-----------------|-------|
| `rr` | `docs/rr/tasks/{slice_id}/` | Mint into open slice; registry + cascade updates that the feature needs are **task obligations** |
| `non_rr` | `.ai/tasks/{feature_id}/` | Mirror task + step sidecars; **no** project-root process/control files under `docs/rr/` |

Scratch stays `.ai/review/<runId>/`, `.ai/refactor/<runId>/` regardless of `project_kind`.

When `payload.feature.artifact_root` is set, durable sidecars resolve under that root — see [slice-pipeline.md](slice-pipeline.md) path abstraction, [plan-schema.md](plan-schema.md), [task-validate.md](task-validate.md).

### Open slice (rr only)

Read current track/slice from `rrr-status.yaml` / prepare cursor / existing `docs/rr/tasks/{slice_id}/`.

| State | Action |
|-------|--------|
| Open slice exists | Mint into `docs/rr/tasks/{slice_id}/` (do **not** mint outside the open slice) |
| rr-project but no open slice | AskQuestion once: pick existing slice dir \| stop — do **not** invent a phantom slice |
| `non_rr` | Skip slice selection; use `feature_id` under `.ai/tasks/` |

## Branch ensure (task-level)

Distinct from per-step [feature-branch.md](feature-branch.md). Run **before** mint commit of work / before plan.

**Name:** `feat/{NNNN}-{short-desc}` (task-dedicated; no step token).

| Predicate | Action |
|-----------|--------|
| HEAD already matches task-dedicated name for this feature (`feat/{NNNN}-{short-desc}`) or engineer confirmed Stay | No-op |
| else | AskQuestion **origin**: `origin/main` \| `origin/master` \| **current branch** → `git checkout -b feat/{NNNN}-{short-desc}` from chosen base |

Dirty tree: carry uncommitted work onto the new branch, or warn per plan-stage pattern — do **not** silent-create without origin AskQuestion when HEAD is not already task-dedicated.

Wire Delivery channels (AskQuestion + text fallback). After branch settled, plan-stage step ensure treats `feat/{NNNN}-*` as Stay-friendly (do not force step rename unless engineer asks).

## Mint

Gate: missing feature intent/desc → one AskQuestion or stop.

### rr

1. Allocate id via [rr-prepare/refs/task-template.md](../rr-prepare/refs/task-template.md) (`docs/rr/tasks/registry.yaml` / max-id under `docs/rr/tasks/`).
2. Write `{NNNN}.md` under the open slice’s `artifact_root` with **Goal** from user intent; **Steps** grain via prepare grain rules (thin L2 — enough to run plan→…→task-validate).
3. Body shape + frontmatter cursor fields per task-template. Upstream doc/ADR/cascade edits the feature requires are **task obligations**, not a separate mode.

### non_rr

1. Choose `feature_id` (kebab from title; unique under `.ai/tasks/`).
2. Allocate `{NNNN}` via local mini-registry or max-id under `.ai/tasks/` only (same monotonic rule, scoped to that tree).
3. Write `{NNNN}.md` + later sidecars under `.ai/tasks/{feature_id}/` with the same body shape as task-template.
4. Follow host conventions from project docs / `AGENTS.md` / code — **never** create `docs/rr/`.

Set cursor on the minted task (`builder_stage` ready for first step **plan**, `step_index: 0`, step done flags false).

## Run loop

1. Set `payload.drive` default `auto` (allow `--manual`); force `payload.scope: task`.
2. Delegate to [slice-pipeline.md](slice-pipeline.md) with cursor on the minted task and durable paths under `artifact_root`.
3. **Hard stop** after task-validate done-when (PASS or hard FAIL) — **never** advance to slice-validate or delivered.

Incompatible with lane flags and with `--slice` / `--next` / `--step` (scope forced to task). See [input-resolution.md](input-resolution.md).

## Done-when

- `project_kind` + `artifact_root` resolved without inventing `docs/rr/` in non-rr repos
- Task minted under the correct root (open slice when rr + open)
- Task branch settled (dedicated name or confirmed Stay)
- Pipeline stopped at task-validate PASS or hard FAIL — no slice-validate / delivered

## Non-goals

- Auto-creating `docs/rr/` via `--feature`
- Running slice-validate / delivered on this path
- Forking a second pipeline (reuse slice-pipeline stages)
- Replacing per-step feature-branch ensure (still runs at plan; Stay-friendly on `feat/{NNNN}-*`)
