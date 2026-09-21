# rr-builder

Slice build **orchestrator** for software engineers: advances an execute-slice under drive×scope (`--auto`\|`--manual` × `--next`\|`--step`\|`--task`\|`--slice`), mints an ad-hoc task via `--feature` (stop at task-validate), or hands off to one nested lane on an explicit flag.

## Why

Execute needs one entry that owns pipeline cursor (prepare → plan → build → refactor → review → validate → optional **ship** → delivered) without preloading every lane rubric, and without silently chaining past an explicit single-lane request or a `--next` intent. Done when the run loop stops (stage done-when, scope boundary, delivered, hard stop, or user decline), or the nested handoff skill finishes.

## What

Owns flag/NL normalization, **orchestrate vs feature vs handoff** mode, drive×scope run loop, `--feature` mint+task-branch ensure, stage→load contracts, plan-stage **feature branch ensure** (`feat/{NNNN}-{step}-{short-desc}`), plan **Ship** intent (`ship_after` / stacked `base`), and on-demand load of `rr-prepare`, `rr-coder`, `rr-tester`, `rr-security-auditor`, `rr-review`, `rr-refactor`, or **rr-ci** on **ship**. **Durable** under `docs/rr/tasks/` or feature `artifact_root` (`.ai/tasks/{feature_id}/` when non-rr). **Scratch:** `.ai/review/<runId>/`, `.ai/refactor/<runId>/`.

**Out of scope:** squash/worktree/prune (those stay **rr-git**); inventing forge CLI (those stay **rr-ci**); README tone rewrites. Mis-invocation redirects live under **Avoid when** only.

## Actions

| id | outcome | pick when |
|----|---------|-----------|
| `feature` | Mint one task → run to task-validate PASS (no slice-validate) | `--feature` / “implement this feature” / “ad-hoc feature” |
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

Defaults: orchestrate without drive/scope → `auto` × `step`. `--feature` → `auto` × forced `task` (allow `--manual`). Lone `--manual` → `scope=step`. Lone `--next` → `drive=manual`. Lone `--step`/`--task`/`--slice` → `drive=auto`. Explicit lane flags ignore drive/scope. `--feature` incompatible with lane flags and with `--slice`/`--next`/`--step`. Reject `--full` → use `--slice`.

## When

### Use when

- Resume or advance a frozen execute-slice through build stages
- Ad-hoc feature work without a prior prepare/slice chain (`--feature`)
- Unattended chain (`--auto`) or single cursor stage (`--next`)
- Prepare a pin-complete slice into ordered tasks
- Implement, test, security-audit, or review a scoped change without full-slice orchestrate
- Need task/slice Goal·Verify / AC validation before ship
- Mid-slice or task-scoped PR via plan **Ship** → forge-miss on validate → **ship** → **rr-ci** → re-validate

### Avoid when

- Cascade planning (exec-summary → PRD) → **rr-planner**
- Forge POST / pipeline debug without a builder ship or review-ci handoff → **rr-ci** directly
- Local git only (rebase, worktree, squash) → **rr-git** (plan-stage / `--feature` branch ensure is **not** this case)
- Docs humanization → **rr-humanize**

## Philosophy

- **Orchestrate by default; feature / handoff on explicit flag** — `--feature` is a third mode (mint + `scope=task`); explicit lane never silently re-enters orchestrate; drive/scope do not mutate handoff lanes
- **Default auto × step** — no drive/scope flags chain the current task-step to step-validate PASS; prepare-only cursor stops after prepare
- **`--feature` stops at task-validate** — never slice-validate / delivered; rr vs non-rr roots (`docs/rr/tasks/` vs `.ai/tasks/`); never invent `docs/rr/` in non-rr repos
- **`--next` unchanged** — lone `--next` is still `manual` × `next`; `--auto --next` runs one stage without confirm
- **Manual never executes without confirm** — AskQuestion (or text fallback) before each stage; under `--slice` the ready list marks cursor stage **`(next)`**; silent chain only with `--auto`
- **Refactor before review** — clean build-touched scope first; orchestrate review is `--fix --all --endless`
- **One nested skill (or stage knowledge set) per stage turn** — never preload all lane skills
- **Plan ≠ build** — plan stage loads knowledge only; no application source edits; plan lands in `{NNNN}-{step}.plan.md` with **Verify hooks** as `- [ ]` checkboxes so build loads one step’s plan, not a bloated task body
- **Feature branch at plan start** — on `main`/`master`, create `feat/{NNNN}-{step}-{short-desc}` before writing the plan; otherwise AskQuestion (stay / new from base / rename / abort) — never invent alternate names or defer to post-build; `--feature` settles `feat/{NNNN}-{short-desc}` first (origin AskQuestion)
- **Ship is planned** — each step plan’s **Ship** sets `branch`, `ship_after`, `base`; `never` = non-shippable (no Forge/PR gate); shippable validate requires an open PR; forge open is **rr-ci** via **ship** before that validate can PASS; `prior_open_pr` stacks onto the latest still-open PR in the `pr_group` chain
- **Refactor lean note** — orchestrate writes `{NNNN}-{step}.refactor.md`; `.ai/refactor/` is scratch only (no required `report.md`)
- **Review under orchestrate is `--fix --all --endless`** — terminal `{NNNN}-{step}.review.md`; scratch under `.ai/review/`; report-only review uses explicit `--review` without `--fix`; handoff `--fix` also forces endless until clear + residual probe
- Orchestrate **review** endless max-epochs without clear → hard stop (`step_review_done` unset)
- Orchestrate **review** success without task `{NNNN}-{step}.review.md` → hard stop (`step_review_done` unset)
- **Validate reports mark checkboxes** — step/task/slice validate persist reports with plan + PASS/FAIL; item PASS flips `- [x]` on plan/task Verify
- **Delivered → residual rr-ci** — mid-slice ships already handed off; delivered only covers unshipped remainder (not used on `--feature`)

## UX

### Invoke

`rr-builder` with `--feature`, or `--auto|--manual` and/or `--next|--step|--task|--slice`, or no flag (defaults `auto` × `step`); or `--prepare|--coder|--tester|--security|--review|--refactor|--add-endless-test`. Nested skills are path-loaded only.

### Intake

Normalize via input-resolution into `payload.mode` (`orchestrate` \| `feature` \| `handoff`) + `drive`/`scope` + optional `feature` / lane/stage (+ optional review/test payloads).

### Clarify

Ambiguous mode → AskQuestion once (feature \| orchestrate drive×scope \| prepare \| coder \| tester \| security \| review \| refactor). Manual → confirm/edit next stage, or ready-vs-blocked pick under `--slice` with cursor stage marked **`(next)`**. Missing kernel/`slice_id`/feature intent → AskQuestion or stop. `--feature` off a task-dedicated branch → origin probe (`origin/main` \| `origin/master` \| current). Plan stage off `main`/`master` → feature-branch probe (stay \| new from base \| rename \| abort). Ship `prior_open_pr` with >1 candidate tip → AskQuestion. Incompatible `--fix` + `--ci` under `--review`, `--endless` + `--ci`, `--feature` + lane/scope flags, `--refactor` + another lane flag, dual drive/scope flags, or `--full` → stop with one-line error.

### Output

Nested skill / stage owns artifacts; `--feature` writes under `artifact_root` (`docs/rr/tasks/{slice_id}/` or `.ai/tasks/{feature_id}/`); prepare writes `docs/rr/tasks/`; orchestrate review/refactor/validate write task sidecars under the active root; `.ai/review/` and `.ai/refactor/` are scratch; validate reports include plan + per-item PASS/FAIL; **ship** persists `active_ship_branch` / `ship_base_branch` then hands off **rr-ci**.

### Close

Stop per drive×scope loop (stage done-when, scope boundary, delivered, hard stop, or decline). `--feature` stops at task-validate. Handoff does not auto-advance the pipeline. Shippable validate forge-miss → **ship** → **rr-ci** → re-validate. Slice validate PASS → **delivered** → residual **rr-ci** only. Load **rr-ci** also after review `--ci`.

## Constraints

- Explicit lane flag wins over cursor; drive/scope ignored on handoff
- `--feature` incompatible with lane flags and with `--slice` / `--next` / `--step`; never invents `docs/rr/` in non-rr repos; never advances past task-validate
- Nested skills are not listed in `plugin.json` — parent **Read**s them
- `--fix` and `--ci` are mutually exclusive under `--review`
- Manual `--slice` never offers **blocked** stages as runnable
- `--refactor` is mutually exclusive with other lane flags (`one lane flag only`)
- Orchestrate **refactor** stage skips when MR ∩ **build-touched** scope is empty (sets `step_refactor_done: true`)
- Orchestrate **review** endless max-epochs without clear → hard stop (`step_review_done` unset)
- Orchestrate **review** success without task `{NNNN}-{step}.review.md` → hard stop (`step_review_done` unset)
- Planning-only docs without implementation or prepare intent → redirect to **rr-planner**

## Notes

Nested lane skills intentionally fail context-engineer `static.name.path-match` — they are path-loaded children of `rr-builder`, not top-level `skills/<name>/` entries.

Layout: `refs/` (router + feature + pipeline + validate + plan allowlist/schema + ship), `rr-prepare/`, `rr-coder/`, `rr-tester/`, `rr-security-auditor/`, `rr-review/`, `rr-refactor/`.

After `--feature` redesign writes: shared write gates (static → reflect → pre-ship → write); recommend post-redesign re-audit on the same path (do not treat prior audit FAILs as mandatory absorb list).
