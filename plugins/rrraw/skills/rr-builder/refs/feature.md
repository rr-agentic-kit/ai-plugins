# Feature mode (planned stages 5–7 runner)

**Audience:** `rr-builder` when `payload.mode: feature`. **SoT** for pipeline preflight → detect → branch ensure → mint → detail → task-scoped run → hard stop at task-validate. Reuses prepare mint templates + [slice-pipeline.md](slice-pipeline.md) — **do not** fork a second stage matrix. [adhoc.md](adhoc.md) thin-wraps this file with urgency bias only.

**Not:** plan-stage [feature-branch.md](feature-branch.md) (per-step `feat/{NNNN}-{step}-*`); product Feature delta / rr-planner Plan; full-slice `--slice`; intake/docs authoring (`refs/planning/intake.md` stages 2–4).

**Pipeline role:** Stages **5–7 runner** for **planned** work — Plan already has (or just absorbed) the surface. Code only after shared intake stages **1–6 PASS** on rr. If stages **2–4 FAIL** → stop and Next Up `--intake` / peer planner — do **not** build.

## Flow

```
situate + pipeline preflight (stages 1–4)
  → if FAIL: stop → Next Up --intake / peer planner SKILL
  → AskQuestion origin if branch not task-dedicated
  → mint / ensure task (rr vs .ai) when stage 5 missing
  → detail Goal/Steps when stage 6 thin
  → set cursor on task
  → run slice-pipeline with scope=task until task-validate PASS
  → stop (no slice-validate / delivered)
```

## Pipeline preflight

Load `refs/planning/intake.md`. Run situate; report **stage reached** and **first blocking stage**.

| `project_kind` | Gate |
|----------------|------|
| `rr` | Stages **2–4** must PASS (docs absorb + cohesion/challenge clear or risk-accepted + select/slice posture). Stages **5–6** may be ensured in this mode (mint + detail). Stage **7** = run loop below. |
| `non_rr` | Collapsed pipeline: situate → mint → detail → code. **Never** invent `docs/rr/`. |

**Refuse and route** when rr stages 2–4 FAIL (docs gap, open cohesion/challenge block, unaddressed impact, no selection/open-slice posture). Do **not** treat missing Plan truth as task-body obligations. Peer Plan work → invoke `skills/rr-planner/SKILL.md` with purpose (`--intake` / `--change` / `--challenge`) — do **not** `Read` planner `refs/*`.

## Detect (`project_kind`)

| Signal | `project_kind` |
|--------|----------------|
| `docs/rr/` present (prefer `docs/rr/rrr-status.yaml` when present) | `rr` |
| else | `non_rr` |

**Never** create `docs/rr/` under `--feature`.

### Artifact root

| `project_kind` | `artifact_root` | Notes |
|----------------|-----------------|-------|
| `rr` | `docs/rr/tasks/{slice_id}/` | Mint into open slice; Plan docs/deltas already absorbed under stages 2–4 — **not** deferred as task obligations |
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

## Mint (stage 5) + detail (stage 6)

Gate: missing intent/desc → one AskQuestion or stop. On rr, only after stages 2–4 PASS.

### rr

1. Allocate id via `skills/s-prepare/refs/task-template.md` (`docs/rr/tasks/registry.yaml` / max-id under `docs/rr/tasks/`).
2. Write `{NNNN}.md` under the open slice’s `artifact_root` with **Goal** from user intent; **Steps** grain via prepare grain rules (thin L2 — enough to run plan→…→task-validate).
3. Body shape + frontmatter cursor fields per task-template. **Obligations cite** absorbed PRD/delta/AC paths — do not invent missing Plan cascade as task-body substitutes for stages 2–4.

### non_rr

1. Choose `feature_id` (kebab from title; unique under `.ai/tasks/`).
2. Allocate `{NNNN}` via local mini-registry or max-id under `.ai/tasks/` only (same monotonic rule, scoped to that tree).
3. Write `{NNNN}.md` + later sidecars under `.ai/tasks/{feature_id}/` with the same body shape as task-template.
4. Follow host conventions from project docs / `AGENTS.md` / code — **never** create `docs/rr/`.

Set cursor on the minted (or detailed) task (`builder_stage` ready for first step **plan**, `step_index: 0`, step done flags false).

## Run loop (stage 7)

1. Set `payload.drive` default `auto` (allow `--manual`); force `payload.scope: task`.
2. Delegate to [slice-pipeline.md](slice-pipeline.md) with cursor on the task and durable paths under `artifact_root`.
3. **Hard stop** after task-validate done-when (PASS or hard FAIL) — **never** advance to slice-validate or delivered.

Incompatible with lane flags and with `--slice` / `--next` / `--step` (scope forced to task). Mutually exclusive with `--intake` and `--adhoc`. See [input-resolution.md](input-resolution.md).

## Done-when

- Pipeline preflight PASS (rr: stages 2–4; non_rr: collapsed) or explicit stop + Next Up intake/planner
- `project_kind` + `artifact_root` resolved without inventing `docs/rr/` in non_rr repos
- Task minted/detailed under the correct root (open slice when rr + open)
- Task branch settled (dedicated name or confirmed Stay)
- Pipeline stopped at task-validate PASS or hard FAIL — no slice-validate / delivered

## Non-goals

- Auto-creating `docs/rr/` via `--feature`
- Code-first / docs-later / obligation-only cascade on rr
- Running slice-validate / delivered on this path
- Forking a second pipeline (reuse slice-pipeline stages)
- Replacing per-step feature-branch ensure (still runs at plan; Stay-friendly on `feat/{NNNN}-*`)
- Skipping intake when stages 2–4 incomplete
- Thin-patching Plan docs inside this mode (Plan absorb → peer planner SKILL entry)
