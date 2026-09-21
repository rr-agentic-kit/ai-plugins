# rr-review

Multi-lane review hub for **rr-builder**. Scratch under **`.ai/review/<runId>/`**; orchestrate terminal under **`docs/rr/tasks/{slice_id}/{NNNN}-{step}.review.md`**.

## Why

Code, test, and security assess need one orchestrator that briefs, chunks, Challenges, and merges — without embedding forge POST scripts. Done when endless/report outcome completes and the terminal path is written: task sidecar when orchestrate supplies cursor, else `REVIEW_DIR/report.md` for handoff without cursor.

## What

Parses lanes, mints `runId`, builds brief, chunks large scope, assesses via nested skills, runs Challenge, then branches to report / inline fix / endless fix loop / **rr-ci** handoff.

**Out of scope:** standalone PR open or pipeline-only debug (**rr-ci** without review); lane rubrics themselves (owned by nested skills).

## When

### Use when

- **rr-builder** `--review` with nested `--code` / `--test` / `--security` / `--all`
- Optional nested `--fix` (inline apply), `--endless` (assess→Challenge→fix until clear; requires `--fix`), or `--ci` (forge POST after Challenge)
- Builder orchestrate **review** stage (forced `--fix --all --endless`; drive/scope per parent)
- "Review my changes" / PR review intent with multi-lane findings

### Avoid when

- Standalone PR open or pipeline-only debug → **rr-ci** without review
- Implement-only or test-only without review flags → route to **rr-coder** / **rr-tester** via parent
- Cascade planning → **rr-planner**

## Philosophy

- **Challenge before consumers** — unchallenged challengeable rows stop the report
- **Keep-only** — consumers use Challenge `keep` rows; dropped observations stay dropped
- **Endless until clear** — `--endless` re-assesses after fix until code+test zero-keep (or security-only `warnings`) or `--max-epochs` (default 5)
- **Scratch vs durable** — `.ai/review/` is in-run; orchestrate task terminal is the durable report
- **Forge handoff** — `--ci` loads **rr-ci** after Challenge; review does not embed glab/gh scripts
- **Parent session** — assess/Challenge runs inline

## UX

### Invoke

Via **rr-builder** `--review` (+ nested flags) or orchestrate **review** stage; parent **Read** when `lane: review`.

### Intake

Parse `refs/params.md` → lanes + outcome (`report` | `fix` | `ci`) + optional `endless` / `max_epochs` + scope/paths.

### Clarify

Empty allowlist → ask once or stop. Optional linked ticket misses must not block when PR/MR or local docs suffice.

### Output

Flat locked filenames under `REVIEW_DIR` scratch (see `refs/artifacts.md`); endless uses epoch-suffixed assess stems; merged scratch `report.md` each epoch; orchestrate also writes `{NNNN}-{step}.review.md`; chat announces the terminal path.

### Close

`--fix` → fix-routing inline; `--endless` → loop per `refs/endless.md`; `--ci` → **rr-ci** after Challenge; refuse POST on unchallenged blocker-tier rows.

## Constraints

- Default lanes: `[code, test, security]` — including `--fix` / report-only with no lane flags; narrow with `--code`/`--test`/`--security`
- `--fix` and `--ci` are mutually exclusive
- `--endless` requires `--fix`; incompatible with `--ci`
- Orchestrate review always forces `--fix --all --endless`
- Scratch `REVIEW_DIR` = `.ai/review/<runId>/` (`runId` = `yyyymmdd-NN` local)
- Orchestrate done-when requires task review sidecar when cursor present
- Security lane is report-only on `--fix`
- `disable-model-invocation: true` / `user-invocable: false`

## Notes

Flag surface under **rr-builder** `--review`: `[--code] [--test] [--security] [--all] [--fix | --ci] [--endless] [--max-epochs <n>] [--scope MR|PR|all|full] [paths…]`. Auto review stage forces `--fix --all --endless`.
