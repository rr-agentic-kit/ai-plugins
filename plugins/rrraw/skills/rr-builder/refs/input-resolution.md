# rr-builder input resolution

**Audience:** Every `rr-builder` invocation. Normalize before orchestrate or handoff.

## Dual mode

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Orchestrate** | `--auto` / `--manual` / `--next` / `--full`, or **no** explicit lane flag | Resolve slice/task cursor → run drive×scope loop ([slice-pipeline.md](slice-pipeline.md)) |
| **Handoff** | `--prepare` \| `--coder` \| `--tester` \| `--security` \| `--review` \| `--refactor` \| `--add-endless-test` | Classify → load **one** nested skill → stop at its done-when (no pipeline advance beyond that skill) |

**Explicit lane flag wins** over drive/scope flags and over `builder_stage` / cursor. When handoff wins, ignore `drive` / `scope` (omit from payload or one-line note: drive/scope ignored for handoff).

## Top-level flags

| Signal | Mode | `payload.mode` | `payload.lane` / stage |
|--------|------|----------------|------------------------|
| Drive/scope flags and/or no lane flag | orchestrate | `orchestrate` | resolve `builder_stage` via cursor |
| `--prepare` | handoff | `handoff` | `prepare` |
| `--coder` | handoff | `handoff` | `coder` |
| `--tester` | handoff | `handoff` | `tester` |
| `--security` (without `--review`) | handoff | `handoff` | `security` |
| `--review` | handoff | `handoff` | `review` (+ nested review flags) |
| `--refactor` | handoff | `handoff` | `refactor` |
| `--add-endless-test` | handoff | `handoff` | `add_endless_test` |

### Drive × scope (orchestrate only)

| Flag | Field | Values |
|------|-------|--------|
| `--auto` \| `--manual` | `payload.drive` | `auto` \| `manual` |
| `--next` \| `--full` | `payload.scope` | `next` \| `full` |

**Defaults:**

| Invocation | `drive` | `scope` |
|------------|---------|---------|
| Orchestrate with neither drive nor scope | `manual` | `full` |
| Lone `--manual` | `manual` | `full` |
| Lone `--full` | `manual` | `full` |
| Lone `--next` | `manual` | `next` |
| Lone `--auto` | `auto` | `full` |
| Both axes present | as stated | as stated |

Conflicting pairs (`--auto` + `--manual`, or `--next` + `--full`) → stop: `one drive flag` / `one scope flag`.

**2×2 behavior** (execution SoT: [slice-pipeline.md](slice-pipeline.md)):

| | `--next` | `--full` |
|---|----------|----------|
| **`--auto`** | Run cursor-next stage; stop when its done-when met | Chain stages until **delivered** or hard stop |
| **`--manual`** | Present next stage; wait for confirm/edit; execute that one | List remaining: **ready** vs **blocked**; mark cursor stage **`(next)`**; AskQuestion among ready; execute chosen; re-list |

**Breaking:** no compat aliases for retired top-level review-only entry flags (`--code` / `--test` / `--all` / `--fix` / `--ci` as sole top-level router). Those nested flags apply **under `--review`** only (or via auto review stage). Multiple explicit lane flags → stop: `one lane flag only`.

## Review flags (under `--review` or auto review stage)

Parse into `payload.review` when `lane: review` **or** when orchestrate stage is **review** (builder forces `--fix --all`):

```yaml
lanes: [code, test, security]   # default --all; narrow with --code / --test / --security
outcome: report | fix | ci        # --fix | --ci; auto review stage forces fix
scope: MR | all                   # --scope MR|PR|all|full
paths: []                         # optional positional narrowers
```

Rules mirror `rr-review/refs/params.md`. Incompatible `--fix` + `--ci` → stop with one-line error.

**Auto review stage:** ignore report-only omission — set `outcome: fix` and `lanes: [code, test, security]`.

## Tester flags (under `--tester` handoff)

When `lane: tester`, pass through normalized flags per `rr-tester/refs/input-resolution.md`. Parent does not re-parse the test conflict matrix.

## Endless test flags (under `--add-endless-test` handoff)

When `lane: add_endless_test`, normalize per `rr-test-endless/refs/input-resolution.md` into `payload.endless_test`. Parent does not run the orchestration loop — hand off to **rr-test-endless** only. Drive/scope ignored.

## Refactor flags (under `--refactor` handoff)

When `lane: refactor`, normalize per `rr-refactor/refs/input-resolution.md` into `payload.refactor`. Parent does not run the epoch loop — hand off to **rr-refactor** only. Drive/scope ignored.

| NL pattern | Lane |
|------------|------|
| "refactor my MR", "behavior-invariant refactor", "clean up god methods on this branch" | `refactor` handoff when clearly refactor-only |

## Plan / slice path

| Input | Payload |
|-------|---------|
| Explicit `execute-slice.yaml` / kernel path | `payload.prepare.kernel_path` |
| `docs/plans/*.md` with implement intent | `payload.plan_path` (orchestrate still prefers task tree under `docs/rr/tasks/`) |
| Cascade dir with `status.yaml` only, no prepare/implement | `OUT_OF_SCOPE` → **rr-planner** |

## Natural language (no lane flag → orchestrate)

| Pattern | Effect |
|---------|--------|
| "continue build", "build the slice", "pick a stage" | `mode: orchestrate`; default `drive: manual`, `scope: full` unless user says otherwise |
| "next stage only", "just the next step" | `mode: orchestrate`, `drive: manual`, `scope: next` |
| "full auto", "chain until delivered", "run through without asking" | `mode: orchestrate`, `drive: auto`, `scope: full` |
| "auto next", "auto one stage" | `mode: orchestrate`, `drive: auto`, `scope: next` |
| "manual", "step by step", "confirm each stage" | `mode: orchestrate`, `drive: manual` (scope stays default `full` unless “next only”) |
| "prepare slice", "decompose execute-slice", "tech plan for slice" | Prefer handoff `prepare` if clearly prepare-only; else orchestrate (cursor may land on prepare) |
| "implement", "write tests only", "OWASP audit", "review my PR", "endless test", "perfect tests loop" **with** clear single-lane intent | AskQuestion once if ambiguous between handoff vs orchestrate; else map to matching handoff lane |
| "refactor my MR", "behavior-invariant refactor", "phased refactor on this branch" | handoff `refactor` when clearly refactor-only (not full-slice orchestrate) |
| Ambiguous | AskQuestion once: orchestrate (auto/manual × next/full) \| prepare \| coder \| tester \| security \| review \| refactor |

## Prepare path

When `lane: prepare` or orchestrate stage **prepare**, resolve `execute-slice.yaml` into `payload.prepare`. Nested skill owns posture + task tree.

```yaml
prepare:
  kernel_path: null | string
  slice_id: null | string
```

## Output payload (skill session)

```yaml
mode: orchestrate | handoff
drive: auto | manual          # orchestrate only; default manual; omit or ignore on handoff
scope: next | full            # orchestrate only; default full; omit or ignore on handoff
lane: null | prepare | coder | tester | security | review | refactor | add_endless_test
builder_stage: null | prepare | plan | build | review | refactor | step_validate | task_validate | slice_validate | delivered
step_index: null | integer
plan_path: null | string
prepare: null | { kernel_path, slice_id }
review: null | { lanes, outcome, scope, paths }
test: null | object   # rr-tester normalized payload
endless_test: null | { max_epochs, max_parallel, start, scope }   # rr-test-endless
refactor: null | { scope, paths, epoch_cap }   # rr-refactor
security_scope: null | { scope, paths }
code_scope: null | { scope, paths, plan_excerpt }
```

## Stop conditions

- Two+ explicit lane flags
- `--auto` and `--manual` together, or `--next` and `--full` together
- `--fix` and `--ci` together (under `--review`)
- No lane/mode and user declines AskQuestion
- Manual gate declined / user declines continue
- Request is clearly **rr-planner** or **rr-ci**-only → redirect per [anti-overlap.md](anti-overlap.md)
- Orchestrate with no pin-complete kernel / no `slice_id` → stop or AskQuestion
- Hard stop from stage failure / validate FAIL (do not chain further under `--full`)
