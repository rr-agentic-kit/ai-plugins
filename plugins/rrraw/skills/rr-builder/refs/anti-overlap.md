# rr-builder anti-overlap

**Audience:** Router and nested skills. Prevents loading wrong plugin skills.

## rr-planner

**Owns:** exec-summary → MRD → BRD → PRD cascade, research, challenge, `docs/plans/status.yaml`.

**rr-builder does not:** compose planning docs, run `agents/planning/*`, or validate cascade format.

**Stop phrase:** "This is planning-only — use **rr-planner**."

## rr-ci

**Owns:** Forge detect, PR/MR title/description, pipeline debug, publish, deploy, inline POST scripts. Disk sidecars under **`.ai/ci/`**.

**When builder hands off:** (1) orchestrate **ship** after planned validate ([ship.md](ship.md) — mid-slice or task-scoped); (2) **slice delivered** residual; (3) **rr-review** `--ci`.

**rr-builder owns:** Slice build **orchestration** (drive×scope: `--auto`/`--manual` × `--next`/`--full`) and explicit lane **handoffs**. Resolves `Ship.branch` / stacked `base` then **Reads** **rr-ci** — does **not** invent forge CLI.

**rr-builder does not:** open MR/PR except by handing off to **rr-ci** (ship stage, delivered residual, or review `--ci`).

**Stop phrase:** "Ship/CI forge mechanics — use **rr-ci**." Builder may **enter** ship and load rr-ci when the step plan declares `ship_after`; it must not skip a planned ship or open the PR itself.

## rr-git

**Owns:** Local git safety, worktrees, squash, conflict resolution, merged branch cleanup.

**rr-builder owns (narrow):** At orchestrate **plan** start, **ensure** the task-step feature branch per [feature-branch.md](feature-branch.md) (`feat/{NNNN}-{step}-{short-desc}`). That is create/checkout (+ optional rename after AskQuestion) only.

**rr-builder may Read** `skills/rr-git/refs/safety.md` when the feature-branch probe chooses rename/`-D`, or worktree refs during review `--fix`. It does **not** replace **rr-git** for squash, worktrees, prune, or standalone git tasks.

**Stop phrase (standalone git):** "Local git only — use **rr-git**." (Does not apply to the plan-stage feature-branch ensure.)

## rr-humanize

**Owns:** Docs register and AI-prose cleanup.

**rr-builder does not:** rewrite marketing or README tone.

## Nested skills

| Skill | Not a substitute for |
|-------|----------------------|
| rr-prepare | rr-planner (product Plan/DEC), rr-coder (implement); owns tech plan + lazy tech ADR gaps + task WBS under `docs/rr/tasks/`; also orchestrate **prepare** stage |
| rr-coder | rr-tester (test strategy), rr-security-auditor (OWASP depth), rr-prepare (task decomposition); plan stage = knowledge only |
| rr-tester | rr-coder (production design), rr-review orchestration, rr-test-endless (multi-epoch loop) |
| rr-test-endless | rr-tester (one-off flags), rr-review `--test --fix` (MR review) |
| rr-security-auditor | rr-coder CPNNN, full test coverage |
| rr-review | rr-ci POST mechanics, host-specific forge/MR scripts; orchestrate review forces `--fix --all` |

**rr-prepare stop phrase:** "Tech plan / task WBS only — use **rr-prepare**; product Plan stays **rr-planner**; code stays **rr-coder**."

**rr-test-endless stop phrase:** "Multi-epoch test perfection loop — use **`rr-builder --add-endless-test`**; one-off test work stays **rr-tester**; MR test-review stays **rr-review**."

## Host-agnostic contract

- Parent session + nested skill Read for review path.
- Artifacts under `.ai/review/<runId>/`.
- No company Jira site assumptions — generic linked ticket/wiki URLs only (`rr-review/refs/brief-sources.md`).
