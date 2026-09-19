# rr-builder

Slice build **orchestrator** for software engineers: advances an execute-slice under drive×scope (`--auto`\|`--manual` × `--next`\|`--full`), or hands off to one nested lane on an explicit flag.

## Why

Execute needs one entry that owns pipeline cursor (prepare → plan → build → review → validate → delivered) without preloading every lane rubric, and without silently chaining past an explicit single-lane request or a `--next` intent. Done when the run loop stops (stage done-when, delivered, hard stop, or user decline), or the nested handoff skill finishes.

## What

Owns flag/NL normalization, **orchestrate vs handoff** mode, drive×scope run loop, stage→load contracts, and on-demand load of `rr-prepare`, `rr-coder`, `rr-tester`, `rr-security-auditor`, or `rr-review`. Prepare/execute cursor under `docs/rr/tasks/`; review artifacts under `.ai/review/<runId>/`.

**Out of scope:** cascade planning; opening PR/MR after delivered (→ **rr-ci**); inventing refactor-stage procedure (TBD stub); standalone git ops; README tone rewrites.

## Actions

| id | outcome | pick when |
|----|---------|-----------|
| `auto` | Orchestrate with `drive=auto` (default `scope=full`) | `--auto` / “full auto” / “chain without asking” |
| `manual` | Orchestrate with confirm before each execute (default drive) | `--manual` / no lane flag / “continue build” |
| `next` | Only cursor-next stage | `--next` / “next stage only” |
| `full` | Remaining stages until **delivered** (default scope) | `--full` / “finish the slice” |
| `prepare` | Tech plan + task WBS via rr-prepare | `--prepare` / prepare-slice NL |
| `coder` | Production implement/refactor via rr-coder | `--coder` / implement-only NL |
| `tester` | Test excellence via rr-tester | `--tester` / test-primary flags |
| `security` | OWASP audit via rr-security-auditor | `--security` without `--review` |
| `review` | Multi-lane assess → report/fix/ci via rr-review | `--review` (+ nested review flags) |

Defaults: orchestrate without drive/scope → `manual` × `full`. Lone `--auto` → `scope=full`. Lone `--next` → `drive=manual`. Explicit lane flags ignore drive/scope.

## When

### Use when

- Resume or advance a frozen execute-slice through build stages
- Unattended chain (`--auto`) or single cursor stage (`--next`)
- Prepare a pin-complete slice into ordered tasks
- Implement, test, security-audit, or review a scoped change without full-slice orchestrate
- Need task/slice Goal·Verify / AC validation before ship

### Avoid when

- Cascade planning (exec-summary → PRD) → **rr-planner**
- PR/MR create, pipeline debug, or forge POST after **delivered** → **rr-ci**
- Local git only (rebase, worktree, squash) → **rr-git**
- Docs humanization → **rr-humanize**

## Philosophy

- **Orchestrate by default; handoff on explicit flag** — explicit never silently re-enters orchestrate; drive/scope do not mutate handoff lanes
- **Default `manual` × `full`** — confirm/pick among remaining stages; silent chain only with `--auto`
- **Manual never executes without confirm** — AskQuestion (or text fallback) before each stage; ready list marks cursor stage **`(next)`**
- **One nested skill (or stage knowledge set) per stage turn** — never preload all lane skills
- **Plan ≠ build** — plan stage loads knowledge only; no application source edits
- **Review under orchestrate is `--fix --all`** — report-only review uses explicit `--review` without `--fix`
- **Delivered → rr-ci** — builder stops at ship boundary

## UX

### Invoke

`rr-builder` with `--auto|--manual` and/or `--next|--full`, or no flag (defaults `manual` × `full`); or `--prepare|--coder|--tester|--security|--review`. Nested skills are path-loaded only.

### Intake

Normalize via input-resolution into `payload.mode` + `drive`/`scope` (orchestrate) + lane/stage (+ optional review/test payloads).

### Clarify

Ambiguous mode → AskQuestion once (orchestrate drive×scope \| prepare \| coder \| tester \| security \| review). Manual → confirm/edit next stage, or ready-vs-blocked pick under `--full` with cursor stage marked **`(next)`**. Missing kernel/`slice_id` → AskQuestion or stop. Incompatible `--fix` + `--ci` under `--review`, or dual drive/scope flags → stop with one-line error.

### Output

Nested skill / stage owns artifacts; prepare writes `docs/rr/tasks/`; review runs write under `.ai/review/<runId>/`; validate stages emit PASS/FAIL verdicts.

### Close

Stop per drive×scope loop (stage done-when, delivered, hard stop, or decline). Handoff does not auto-advance the pipeline. Slice validate PASS → **delivered** → point to **rr-ci**. Load **rr-ci** mid-builder only after review `--ci` or explicit ship request.

## Constraints

- Explicit lane flag wins over cursor; drive/scope ignored on handoff
- Nested skills are not listed in `plugin.json` — parent **Read**s them
- `--fix` and `--ci` are mutually exclusive under `--review`
- Manual `--full` never offers **blocked** stages as runnable
- Refactor stage is TBD (skip or stop — do not invent)
- Planning-only docs without implementation or prepare intent → redirect to **rr-planner**

## Notes

Nested lane skills intentionally fail context-engineer `static.name.path-match` — they are path-loaded children of `rr-builder`, not top-level `skills/<name>/` entries.

Layout: `refs/` (router + pipeline + validate), `rr-prepare/`, `rr-coder/`, `rr-tester/`, `rr-security-auditor/`, `rr-review/`.
