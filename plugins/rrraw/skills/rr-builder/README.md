# rr-builder

Slice build **orchestrator** for software engineers: advances an execute-slice under drive×scope (`--auto`\|`--manual` × `--next`\|`--step`\|`--task`\|`--slice`), or hands off to one nested lane on an explicit flag.

## Why

Execute needs one entry that owns pipeline cursor (prepare → plan → build → refactor → review → validate → optional **ship** → delivered) without preloading every lane rubric, and without silently chaining past an explicit single-lane request or a `--next` intent. Done when the run loop stops (stage done-when, scope boundary, delivered, hard stop, or user decline), or the nested handoff skill finishes.

## What

Owns flag/NL normalization, **orchestrate vs handoff** mode, drive×scope run loop, stage→load contracts, plan-stage **feature branch ensure** (`feat/{NNNN}-{step}-{short-desc}`), plan **Ship** intent (`ship_after` / stacked `base`), and on-demand load of `rr-prepare`, `rr-coder`, `rr-tester`, `rr-security-auditor`, `rr-review`, `rr-refactor`, or **rr-ci** on **ship**. Prepare/execute cursor under `docs/rr/tasks/`; review artifacts under `.ai/review/<runId>/`; refactor under `.ai/refactor/<runId>/`.

**Out of scope:** squash/worktree/prune (those stay **rr-git**); inventing forge CLI (those stay **rr-ci**); README tone rewrites. Mis-invocation redirects live under **Avoid when** only.

## Actions

| id | outcome | pick when |
|----|---------|-----------|
| `auto` | Orchestrate with `drive=auto` (default `scope=step`) | `--auto` / “full auto” / “chain without asking” |
| `manual` | Orchestrate with confirm before each execute | `--manual` / “confirm each stage” |
| `next` | Only cursor-next stage | `--next` / “next stage only” |
| `step` | Current task-step through step-validate PASS (default scope) | `--step` / “one step” / “continue step” |
| `task` | Active task through task-validate PASS | `--task` / “finish this task” |
| `slice` | Remaining stages until **delivered** | `--slice` / “finish the slice” (replaces retired `--full`) |
| `prepare` | Tech plan + task WBS via rr-prepare | `--prepare` / prepare-slice NL |
| `coder` | Production implement/refactor via rr-coder | `--coder` / implement-only NL |
| `tester` | Test excellence via rr-tester | `--tester` / test-primary flags |
| `security` | OWASP audit via rr-security-auditor | `--security` without `--review` |
| `review` | Multi-lane assess → report/fix/endless/ci via rr-review | `--review` (+ nested review flags) |
| `refactor` | Fixed-point behavior-invariant coder-rule refactor via rr-refactor | `--refactor` (+ optional `--scope`, `--epoch-cap`, paths) |
| `add_endless_test` | Coverage-first multi-epoch test loop via rr-test-endless | `--add-endless-test` |

Defaults: orchestrate without drive/scope → `auto` × `step`. Lone `--manual` → `scope=step`. Lone `--next` → `drive=manual`. Lone `--step`/`--task`/`--slice` → `drive=auto`. Explicit lane flags ignore drive/scope. Reject `--full` → use `--slice`.

## When

### Use when

- Resume or advance a frozen execute-slice through build stages
- Unattended chain (`--auto`) or single cursor stage (`--next`)
- Prepare a pin-complete slice into ordered tasks
- Implement, test, security-audit, or review a scoped change without full-slice orchestrate
- Need task/slice Goal·Verify / AC validation before ship
- Mid-slice or task-scoped PR via plan **Ship** → forge-miss on validate → **ship** → **rr-ci** → re-validate

### Avoid when

- Cascade planning (exec-summary → PRD) → **rr-planner**
- Forge POST / pipeline debug without a builder ship or review-ci handoff → **rr-ci** directly
- Local git only (rebase, worktree, squash) → **rr-git** (plan-stage feature-branch ensure is **not** this case)
- Docs humanization → **rr-humanize**

## Philosophy

- **Orchestrate by default; handoff on explicit flag** — explicit never silently re-enters orchestrate; drive/scope do not mutate handoff lanes
- **Default auto × step** — no drive/scope flags chain the current task-step to step-validate PASS; prepare-only cursor stops after prepare
- **`--next` unchanged** — lone `--next` is still `manual` × `next`; `--auto --next` runs one stage without confirm
- **Manual never executes without confirm** — AskQuestion (or text fallback) before each stage; under `--slice` the ready list marks cursor stage **`(next)`**; silent chain only with `--auto`
- **Refactor before review** — clean build-touched scope first; orchestrate review is `--fix --all --endless`
- **One nested skill (or stage knowledge set) per stage turn** — never preload all lane skills
- **Plan ≠ build** — plan stage loads knowledge only; no application source edits; plan lands in `{NNNN}-{step}.plan.md` (1-based step) so build loads one step’s plan, not a bloated task body
- **Feature branch at plan start** — on `main`/`master`, create `feat/{NNNN}-{step}-{short-desc}` before writing the plan; otherwise AskQuestion (stay / new from base / rename / abort) — never invent alternate names or defer to post-build
- **Ship is planned** — each step plan’s **Ship** sets `branch`, `ship_after`, `base`; `never` = non-shippable (no Forge/PR gate); shippable validate requires an open PR; forge open is **rr-ci** via **ship** before that validate can PASS; `prior_open_pr` stacks onto the latest still-open PR in the `pr_group` chain
- **Review under orchestrate is `--fix --all --endless`** — report-only review uses explicit `--review` without `--fix`
- **Delivered → residual rr-ci** — mid-slice ships already handed off; delivered only covers unshipped remainder

## UX

### Invoke

`rr-builder` with `--auto|--manual` and/or `--next|--step|--task|--slice`, or no flag (defaults `auto` × `step`); or `--prepare|--coder|--tester|--security|--review|--refactor|--add-endless-test`. Nested skills are path-loaded only.

### Intake

Normalize via input-resolution into `payload.mode` + `drive`/`scope` (orchestrate) + lane/stage (+ optional review/test payloads).

### Clarify

Ambiguous mode → AskQuestion once (orchestrate drive×scope \| prepare \| coder \| tester \| security \| review \| refactor). Manual → confirm/edit next stage, or ready-vs-blocked pick under `--slice` with cursor stage marked **`(next)`**. Missing kernel/`slice_id` → AskQuestion or stop. Plan stage off `main`/`master` → feature-branch probe (stay \| new from base \| rename \| abort). Ship `prior_open_pr` with >1 candidate tip → AskQuestion. Incompatible `--fix` + `--ci` under `--review`, `--endless` + `--ci`, `--refactor` + another lane flag, dual drive/scope flags, or `--full` → stop with one-line error.

### Output

Nested skill / stage owns artifacts; prepare writes `docs/rr/tasks/`; review runs write under `.ai/review/<runId>/`; refactor runs write under `.ai/refactor/<runId>/`; validate stages emit PASS/FAIL verdicts; **ship** persists `active_ship_branch` / `ship_base_branch` then hands off **rr-ci**.

### Close

Stop per drive×scope loop (stage done-when, scope boundary, delivered, hard stop, or decline). Handoff does not auto-advance the pipeline. Shippable validate forge-miss → **ship** → **rr-ci** → re-validate. Slice validate PASS → **delivered** → residual **rr-ci** only. Load **rr-ci** also after review `--ci`.

## Constraints

- Explicit lane flag wins over cursor; drive/scope ignored on handoff
- Nested skills are not listed in `plugin.json` — parent **Read**s them
- `--fix` and `--ci` are mutually exclusive under `--review`
- Manual `--slice` never offers **blocked** stages as runnable
- `--refactor` is mutually exclusive with other lane flags (`one lane flag only`)
- Orchestrate **refactor** stage skips when MR ∩ **build-touched** scope is empty (sets `step_refactor_done: true`)
- Orchestrate **review** endless max-epochs without clear → hard stop (`step_review_done` unset)
- Planning-only docs without implementation or prepare intent → redirect to **rr-planner**

## Notes

Nested lane skills intentionally fail context-engineer `static.name.path-match` — they are path-loaded children of `rr-builder`, not top-level `skills/<name>/` entries.

Layout: `refs/` (router + pipeline + validate + plan allowlist/schema + ship), `rr-prepare/`, `rr-coder/`, `rr-tester/`, `rr-security-auditor/`, `rr-review/`, `rr-refactor/`.
