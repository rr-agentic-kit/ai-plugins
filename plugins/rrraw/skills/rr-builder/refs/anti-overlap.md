# rr-builder anti-overlap

**Audience:** Router and nested skills. Prevents loading wrong plugin skills.

## rr-planner

**Owns:** exec-summary → MRD → BRD → PRD cascade, research, challenge, `docs/plans/status.yaml`.

**rr-builder does not:** compose planning docs, run `agents/planning/*`, or validate cascade format.

**`--feature` ≠ product Plan:** ad-hoc `--feature` mints one execute task and runs to task-validate ([feature.md](feature.md)) — it does **not** author cascade/PRD or replace **rr-planner**. Upstream cascade/docs edits required by the feature are **task obligations**, not a Plan phase.

**`--feature` ≠ full-slice `--slice`:** stops at task-validate; never slice-validate / delivered on this path.

**Stop phrase:** "This is planning-only — use **rr-planner**."
## s-ci

**Owns:** Forge detect, PR/MR title/description, pipeline debug, publish, deploy, inline POST scripts. Disk sidecars under **`.ai/ci/`**.

**When builder hands off:** (1) orchestrate **ship** after planned validate ([ship.md](ship.md) — mid-slice or task-scoped); (2) **pr-validate** wait/fix probes (`pre-merge-status`, `debug-pipeline`, `--fix --sonar`) after forge landing push ([pr-validate.md](pr-validate.md)); (3) **slice delivered** residual; (4) **s-review** `--ci`.

**rr-builder owns:** Slice build **orchestration** (drive×scope: `--auto`/`--manual` × `--next`/`--step`/`--task`/`--slice`), ad-hoc **`--feature`** (mint + `scope=task`), and explicit lane **handoffs**. Resolves `Ship.branch` / stacked `base` then **Reads** **s-ci** — does **not** invent forge CLI. **pr-validate:** builder waits/orchestrates; s-ci owns wait probes + Sonar fix.
**rr-builder does not:** open MR/PR except by handing off to **s-ci** (ship stage, delivered residual, or review `--ci`); invent forge wait CLI or list Sonar issues itself.

**Stop phrase:** "Ship/CI forge mechanics — use **s-ci**." Builder may **enter** ship and load s-ci when shippable validate hits the Forge/PR gate (or plan declares `ship_after`); it must not skip a planned ship, require PASS-before-ship for that gate, or open the PR itself. After tip push, builder enters **pr-validate** and load s-ci for status/fix — it must not invent wait flags or treat Sonar as ad-hoc outside `--fix --sonar`.

**Forge-open invariant SoT:** the two s-ci bullets above ("When builder hands off" + "does not open MR/PR except by handing off"). Other refs (ship.md, task-validate.md, slice-pipeline.md, routing.md, SKILL.md) carry pointers only.

## s-git

**Owns:** Local git safety, worktrees, squash, conflict resolution, merged branch cleanup.

**rr-builder owns (narrow):** (1) **`--feature`** task-branch ensure per [feature.md](feature.md) (`feat/{NNNN}-{short-desc}` + origin AskQuestion). (2) At orchestrate **plan** start, **ensure** the task-step feature branch per [feature-branch.md](feature-branch.md) (`feat/{NNNN}-{step}-{short-desc}`). Both are create/checkout (+ optional rename/origin after AskQuestion) only — not squash/worktree/prune.
**rr-builder may Read** `skills/s-git/refs/safety.md` when the feature-branch probe chooses rename/`-D`, or worktree refs during review `--fix`. It does **not** replace **s-git** for squash, worktrees, prune, or standalone git tasks.

**Stop phrase (standalone git):** "Local git only — use **s-git**." (Does not apply to the plan-stage feature-branch ensure.)

## s-humanize

**Owns:** Docs register and AI-prose cleanup.

**rr-builder does not:** rewrite marketing or README tone.

## Nested skills

| Skill | Not a substitute for |
|-------|----------------------|
| s-prepare | rr-planner (product Plan/DEC), s-coder (implement); owns tech plan + lazy tech ADR gaps + task WBS under `docs/rr/tasks/`; also orchestrate **prepare** stage |
| s-coder | s-tester (test strategy), s-security (OWASP depth), s-prepare (task decomposition); plan stage = knowledge only |
| s-tester | s-coder (production design), s-review orchestration, s-test-endless (multi-epoch loop) |
| s-test-endless | s-tester (one-off flags), s-review `--test --fix` (MR review) |
| s-security | s-coder CPNNN, full test coverage |
| s-review | s-ci POST mechanics, host-specific forge/MR scripts; orchestrate review forces `--fix --all --endless` |

**s-prepare stop phrase:** "Tech plan / task WBS only — use **s-prepare**; product Plan stays **rr-planner**; code stays **s-coder**."

**s-test-endless stop phrase:** "Multi-epoch test perfection loop — use **`rr-builder --add-endless-test`**; one-off test work stays **s-tester**; MR test-review stays **s-review**."

## Host-agnostic contract

- Parent session + nested skill Read for review path.
- Artifacts under `.ai/review/<runId>/`.
- No company Jira site assumptions — generic linked ticket/wiki URLs only (`s-review/refs/brief-sources.md`).
