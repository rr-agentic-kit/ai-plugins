# rr-builder input resolution

**Audience:** Every `rr-builder` invocation. Normalize before orchestrate, intake, feature, adhoc, or handoff.

## Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Intake** | `--intake` (or NL idea / coverage / “build X” on rr that needs docs/pipeline) | Walk stages 1→7 per [intake-absorb.md](intake-absorb.md); peer planner SKILL for 2–4 when needed; may continue to `--feature` / `--adhoc` when unblocked |
| **Feature** | `--feature` (or NL planned implement when pipeline already clear) | Pipeline preflight → mint/detail if needed → run `drive` × `scope=task` until task-validate ([feature.md](feature.md)); hard stop — no slice-validate/delivered. Refuse if rr stages 2–4 FAIL → Next Up `--intake` |
| **Adhoc** | `--adhoc` (or NL urgent/unplanned implement when pipeline already clear) | Same runner as feature via [adhoc.md](adhoc.md) urgency wrap; same gates. Refuse if rr stages 2–4 FAIL → Next Up `--intake` |
| **Orchestrate** | `--auto` / `--manual` / `--next` / `--step` / `--task` / `--slice`, or **no** explicit lane/`--intake`/`--feature`/`--adhoc` flag | Resolve slice/task cursor → run drive×scope loop ([slice-pipeline.md](slice-pipeline.md)) |
| **Handoff** | `--prepare` \| `--coder` \| `--tester` \| `--security` \| `--review` \| `--refactor` \| `--add-endless-test` | Classify → load **one** nested skill → stop at its done-when (no pipeline advance beyond that skill) |

**Explicit lane flag wins** over drive/scope flags and over `builder_stage` / cursor. When handoff wins, ignore `drive` / `scope` (omit from payload or one-line note: drive/scope ignored for handoff). **`--intake` / `--feature` / `--adhoc` win** over bare orchestrate defaults; mutually exclusive with each other; incompatible with lane flags and with `--slice` / `--next` / `--step`. NL: idea/coverage/docs-gap → `--intake`; planned feature/PRD id → `--feature`; urgent/unplanned/interrupt → `--adhoc`.

## Top-level flags

| Signal | Mode | `payload.mode` | `payload.lane` / stage |
|--------|------|----------------|------------------------|
| `--intake` | intake | `intake` | situate → peer planner for 2–4 → … per intake-absorb |
| `--feature` | feature | `feature` | planned mint + task run after preflight; see Feature mode below |
| `--adhoc` | adhoc | `adhoc` | urgent mint + task run after preflight; see Adhoc mode below |
| Drive/scope flags and/or no lane/`--intake`/`--feature`/`--adhoc` flag | orchestrate | `orchestrate` | resolve `builder_stage` via cursor |
| `--prepare` | handoff | `handoff` | `prepare` |
| `--coder` | handoff | `handoff` | `coder` |
| `--tester` | handoff | `handoff` | `tester` |
| `--security` (without `--review`) | handoff | `handoff` | `security` |
| `--review` | handoff | `handoff` | `review` (+ nested review flags) |
| `--refactor` | handoff | `handoff` | `refactor` |
| `--add-endless-test` | handoff | `handoff` | `add_endless_test` |

### Intake mode (`--intake`)

Procedure SoT: [intake-absorb.md](intake-absorb.md) + shared `refs/planning/intake.md`.

| Rule | Detail |
|------|--------|
| Drive/scope | Omit until continuing into feature/adhoc run; then default `auto` × forced `task` |
| Lanes | Incompatible with any lane flag → stop: `intake incompatible with lane flags` |
| Peer | Stages 2–4 via peer `skills/rr-planner/SKILL.md` (Task or Read SKILL + purpose) — not planner refs |
| Intent | Missing title/desc → one AskQuestion or stop |
| Code | Only after stages 1–6 PASS |

### Feature mode (`--feature`)

Top-level path (not a lane handoff). Procedure SoT: [feature.md](feature.md).

| Rule | Detail |
|------|--------|
| Drive | Default `auto`; allow `--manual` only among drive/scope flags |
| Scope | Forced `task` — reject `--slice` / `--next` / `--step` with one-line stop |
| Lanes | Incompatible with any lane flag → stop: `feature incompatible with lane flags` |
| Intent | Missing title/desc → one AskQuestion or stop |
| Preflight | rr stages 2–4 FAIL → stop + Next Up `--intake` / peer planner (do not mint-to-code) |
| Payload | `payload.feature` (see Output payload) |

```yaml
feature:
  title: string              # or desc from NL
  project_kind: rr | non_rr  # docs/rr/ present → rr
  artifact_root: string      # docs/rr/tasks/{slice_id}/ | .ai/tasks/{feature_id}/
  slice_id: null | string    # rr + open slice only
  feature_id: string         # non_rr dir stem; rr may mirror short-desc
  branch: string             # feat/{NNNN}-{short-desc} when created/settled
  base: string               # origin/main | origin/master | current branch name
```

### Adhoc mode (`--adhoc`)

Same runner as feature; urgency wrap SoT: [adhoc.md](adhoc.md) → [feature.md](feature.md).

| Rule | Detail |
|------|--------|
| Drive / scope / lanes / intent / preflight | Same matrix as Feature mode (`adhoc incompatible with lane flags`) |
| Payload | `payload.adhoc` (same shape as `feature`, with `adhoc_id` instead of `feature_id`) |

```yaml
adhoc:
  title: string
  project_kind: rr | non_rr
  artifact_root: string      # docs/rr/tasks/{slice_id}/ | .ai/tasks/{adhoc_id}/
  slice_id: null | string
  adhoc_id: string
  branch: string
  base: string
```

### Drive × scope (orchestrate only)


| Flag | Field | Values |
|------|-------|--------|
| `--auto` \| `--manual` | `payload.drive` | `auto` \| `manual` |
| `--next` \| `--step` \| `--task` \| `--slice` | `payload.scope` | `next` \| `step` \| `task` \| `slice` |

**Defaults:**

| Invocation | `drive` | `scope` |
|------------|---------|---------|
| Orchestrate with neither drive nor scope | `auto` | `step` |
| Lone `--manual` | `manual` | `step` |
| Lone `--auto` | `auto` | `step` |
| Lone `--next` | `manual` | `next` |
| Lone `--step` / `--task` / `--slice` | `auto` | as stated |
| `--auto --next` | `auto` | `next` |
| Both axes otherwise | as stated | as stated |

Conflicting pairs (`--auto` + `--manual`, or any two of `--next` \| `--step` \| `--task` \| `--slice`) → stop: `one drive flag` / `one scope flag`.

Reject retired `--full` with one-line: `use --slice` (no alias).

**Drive × scope behavior** (execution SoT: [slice-pipeline.md](slice-pipeline.md)):

| | `--next` | `--step` | `--task` | `--slice` |
|---|----------|----------|----------|-----------|
| **`--auto`** | Run cursor-next stage; stop when its done-when met | Chain until step boundary: non-final → step-validate PASS; **final** step (or cursor on `task_validate`) → task-validate PASS ≡ `--task` for that run (prepare-only: stop after prepare) | **Task run** ([task-run.md](task-run.md)), or **Isolated step run** for step-granularity tasks ([slice-pipeline.md](slice-pipeline.md)), until task-validate PASS | Same loop per task, then parent validate until **delivered** or hard stop |
| **`--manual`** | Present next stage; wait for confirm/edit; execute that one | Same step boundary (incl. last-step ≡ task); AskQuestion before each stage | Same task boundary; AskQuestion before each stage | Ready vs **blocked**; mark cursor **`(next)`**; AskQuestion among ready; re-list until boundary / decline / hard stop |

**Breaking:** no compat aliases for retired top-level review-only entry flags (`--code` / `--test` / `--all` / `--fix` / `--ci` as sole top-level router). Those nested flags apply **under `--review`** only (or via auto review stage). Multiple explicit lane flags → stop: `one lane flag only`.

## Review flags (under `--review` or auto review stage)

Parse into `payload.review` when `lane: review` **or** when orchestrate stage is **review** (builder forces `--fix --all --endless`):

```yaml
lanes: [code, test, security]   # default --all (also when --fix / report-only with no lane flags)
outcome: report | fix | ci        # --fix | --ci; auto review stage forces fix
endless: false | true             # forced true when outcome: fix (--fix or auto); --endless alone still forces fix
max_epochs: 5                     # --max-epochs; default 5 when endless
scope: MR | all                   # --scope MR|PR|all|full
paths: []                         # optional positional narrowers
```

Rules mirror `skills/s-review/refs/params.md`. Incompatible `--fix` + `--ci` → stop with one-line error. `--endless` + `--ci` → stop. `--endless` without `--fix` under handoff → stop or force `outcome: fix`. **Handoff `--fix` forces `endless: true`** (same as auto) — do not run single-shot fix-then-exit.

**Auto review stage:** ignore report-only omission — set `outcome: fix`, `lanes: [code, test, security]`, `endless: true`, `max_epochs: 5` (or parsed `--max-epochs`).

## Tester flags (under `--tester` handoff)

When `lane: tester`, pass through normalized flags per `skills/s-tester/refs/input-resolution.md`. Parent does not re-parse the test conflict matrix.

## Endless test flags (under `--add-endless-test` handoff)

When `lane: add_endless_test`, normalize per `skills/s-test-endless/refs/input-resolution.md` into `payload.endless_test`. Parent does not run the orchestration loop — hand off to **s-test-endless** only. Drive/scope ignored.

## Refactor flags (under `--refactor` handoff)

When `lane: refactor`, normalize per `skills/s-refactor/refs/input-resolution.md` into `payload.refactor`. Parent does not run the epoch loop — hand off to **s-refactor** only. Drive/scope ignored.

| NL pattern | Lane |
|------------|------|
| "refactor my MR", "behavior-invariant refactor", "clean up god methods on this branch" | `refactor` handoff when clearly refactor-only |

## Plan / slice path

| Input | Payload |
|-------|---------|
| Explicit `execute-slice.yaml` / kernel path | `payload.prepare.kernel_path` |
| `docs/plans/*.md` with implement intent | `payload.plan_path` (orchestrate still prefers task tree under `docs/rr/tasks/`) |
| Cascade dir with `status.yaml` only, no prepare/implement | `OUT_OF_SCOPE` → **rr-planner** |

## Natural language (no lane flag → orchestrate, intake, feature, or adhoc)

| Pattern | Effect |
|---------|--------|
| "intake", "coverage check", "add this requirement", "idea for X", "build X" on rr when docs/cohesion unclear | `mode: intake` |
| "implement planned feature", "implement feature X", PRD/requirement id, selected requirement ready | `mode: feature` when stages 2–4 PASS or `non_rr`; else `mode: intake` |
| "urgent", "unplanned", "interrupt", "ship this now", "implement this adhoc", "ad-hoc task" | `mode: adhoc` when pipeline clear / gates PASS; else `mode: intake` |
| "ad-hoc feature" (legacy phrasing) | Prefer `mode: intake` on rr unless urgency words → `adhoc`, or planned surface clear → `feature` |
| "continue build", "build the slice", "pick a stage" | `mode: orchestrate`; default `drive: auto`, `scope: step` unless user says otherwise |
| "next stage only", "just the next step" | `mode: orchestrate`, `drive: manual`, `scope: next` |
| "auto next", "auto one stage" | `mode: orchestrate`, `drive: auto`, `scope: next` |
| "one step", "continue step", "finish this step" | `mode: orchestrate`, `drive: auto`, `scope: step` (final step ≡ `--task` through task-validate) |
| "finish this task", "complete the task" | `mode: orchestrate`, `drive: auto`, `scope: task` |
| "full auto", "finish the slice", "chain until delivered", "run through without asking" | `mode: orchestrate`, `drive: auto`, `scope: slice` |
| "manual", "step by step", "confirm each stage" | `mode: orchestrate` or `feature`/`adhoc`/`intake` if already that intent; `drive: manual` (orchestrate scope stays default `step` unless “next only” / “finish task” / “finish slice”) |
| "prepare slice", "decompose execute-slice", "tech plan for slice" | Prefer handoff `prepare` if clearly prepare-only; else orchestrate (cursor may land on prepare) |
| "implement", "write tests only", "OWASP audit", "review my PR", "endless test", "perfect tests loop" **with** clear single-lane intent | AskQuestion once if ambiguous between handoff vs orchestrate vs intake/feature/adhoc; else map to matching handoff lane |
| "refactor my MR", "behavior-invariant refactor", "phased refactor on this branch" | handoff `refactor` when clearly refactor-only (not full-slice orchestrate) |
| Ambiguous | AskQuestion once: intake \| feature \| adhoc \| orchestrate (auto/manual × next/step/task/slice) \| prepare \| coder \| tester \| security \| review \| refactor |

## Prepare path

When `lane: prepare` or orchestrate stage **prepare**, resolve `execute-slice.yaml` into `payload.prepare`. Nested skill owns posture + task tree.

```yaml
prepare:
  kernel_path: null | string
  slice_id: null | string
```

## Output payload (skill session)

```yaml
mode: orchestrate | intake | feature | adhoc | handoff
drive: auto | manual          # orchestrate + feature + adhoc; default auto; omit or ignore on handoff/intake until feature/adhoc continue
scope: next | step | task | slice   # orchestrate: default step; feature/adhoc: forced task; omit or ignore on handoff/intake until continue
lane: null | prepare | coder | tester | security | review | refactor | add_endless_test
feature: null | { title, project_kind, artifact_root, slice_id, feature_id, branch, base }
adhoc: null | { title, project_kind, artifact_root, slice_id, adhoc_id, branch, base }
builder_stage: null | prepare | plan | build | refactor | review | step_validate | task_validate | slice_validate | delivered
step_index: null | integer
plan_path: null | string
prepare: null | { kernel_path, slice_id }
review: null | { lanes, outcome, endless, max_epochs, scope, paths }
test: null | object   # s-tester normalized payload
endless_test: null | { max_epochs, max_parallel, start, scope }   # s-test-endless
refactor: null | { scope, paths, epoch_cap }   # s-refactor
security_scope: null | { scope, paths }
code_scope: null | { scope, paths, plan_excerpt }
```

## Stop conditions

- Two+ explicit lane flags
- `--intake` or `--feature` or `--adhoc` + any lane flag
- `--intake` or `--feature` or `--adhoc` + `--slice` / `--next` / `--step`
- Any two of `--intake` / `--feature` / `--adhoc` together
- `--auto` and `--manual` together, or any two of `--next` / `--step` / `--task` / `--slice`
- Retired `--full` present → `use --slice`
- `--fix` and `--ci` together (under `--review`)
- `--endless` and `--ci` together (under `--review`)
- `--feature` / `--adhoc` / `--intake` with missing intent/desc and user declines AskQuestion
- `--feature` / `--adhoc` on rr when stages 2–4 FAIL (route intake / peer planner)
- No lane/mode and user declines AskQuestion
- Manual gate declined / user declines continue
- Request is clearly **rr-planner** or **s-ci**-only → redirect per [anti-overlap.md](anti-overlap.md)
- Orchestrate with no pin-complete kernel / no `slice_id` → stop or AskQuestion
- Hard stop from stage failure / validate FAIL / endless review max-epochs without clear exit (do not chain further under `step` / `task` / `slice`)
- Feature / adhoc mode after task-validate done-when — do not chain to slice-validate / delivered
- Intake stage-3 block — do not code; peer-invoke planner/discovery