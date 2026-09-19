# rr-builder anti-overlap

**Audience:** Router and nested skills. Prevents loading wrong plugin skills.

## rr-planner

**Owns:** exec-summary → MRD → BRD → PRD cascade, research, challenge, `docs/plans/status.yaml`.

**rr-builder does not:** compose planning docs, run `agents/planning/*`, or validate cascade format.

**Stop phrase:** "This is planning-only — use **rr-planner**."

## rr-ci

**Owns:** Forge detect, PR/MR title/description, pipeline debug, publish, deploy, inline POST scripts. Disk sidecars under **`.ai/ci/`**. Ship after **slice delivered**.

**rr-builder owns:** Slice build **orchestration** (drive×scope: `--auto`/`--manual` × `--next`/`--full`) and explicit lane **handoffs**. Stops at delivered — does **not** open MR/PR from orchestrate.

**rr-builder does not:** open MR/PR except when **rr-review** handoff finished with `--ci` and hands off to **rr-ci**.

**Stop phrase:** "Ship/CI only — use **rr-ci**." After slice validate PASS → delivered boundary → **rr-ci**. Review first if user wants findings before POST.

## rr-git

**Owns:** Local git safety, worktrees, squash, conflict resolution, merged branch cleanup.

**rr-builder may Read** `skills/rr-git/refs/safety.md` or worktree refs during review `--fix`; it does not replace **rr-git** for standalone git tasks.

## rr-humanize

**Owns:** Docs register and AI-prose cleanup.

**rr-builder does not:** rewrite marketing or README tone.

## Nested skills

| Skill | Not a substitute for |
|-------|----------------------|
| rr-prepare | rr-planner (product Plan/DEC), rr-coder (implement); owns tech plan + lazy tech ADR gaps + task WBS under `docs/rr/tasks/`; also orchestrate **prepare** stage |
| rr-coder | rr-tester (test strategy), rr-security-auditor (OWASP depth), rr-prepare (task decomposition); plan stage = knowledge only |
| rr-tester | rr-coder (production design), rr-review orchestration |
| rr-security-auditor | rr-coder CPNNN, full test coverage |
| rr-review | rr-ci POST mechanics, host-specific forge/MR scripts; orchestrate review forces `--fix --all` |

**rr-prepare stop phrase:** "Tech plan / task WBS only — use **rr-prepare**; product Plan stays **rr-planner**; code stays **rr-coder**."

## Host-agnostic contract

- Parent session + nested skill Read for review path.
- Artifacts under `.ai/review/<runId>/`.
- No company Jira site assumptions — generic linked ticket/wiki URLs only (`rr-review/refs/brief-sources.md`).
