# rr-builder anti-overlap

**Audience:** Router and nested skills. Prevents loading wrong plugin skills.

## rr-planner

**Owns:** exec-summary → MRD → BRD → PRD cascade, research, challenge, `docs/plans/status.yaml`.

**rr-builder does not:** compose planning docs, run `agents/planning/*`, or validate cascade format.

**Stop phrase:** "This is planning-only — use **rr-planner**."

## rr-ci

**Owns:** Forge detect, PR/MR title/description, pipeline debug, publish, deploy, inline POST scripts.

**rr-builder does not:** open MR/PR except when **rr-review** finished with `--ci` and hands off to **rr-ci**.

**Stop phrase:** "Ship/CI only — use **rr-ci**." Review first if user wants findings before POST.

## rr-git

**Owns:** Local git safety, worktrees, squash, conflict resolution, merged branch cleanup.

**rr-builder may Read** `skills/rr-git/refs/safety.md` or worktree refs during review `--fix`; it does not replace **rr-git** for standalone git tasks.

## rr-humanize

**Owns:** Docs register and AI-prose cleanup.

**rr-builder does not:** rewrite marketing or README tone.

## Nested skills

| Skill | Not a substitute for |
|-------|----------------------|
| rr-coder | rr-tester (test strategy), rr-security-auditor (OWASP depth) |
| rr-tester | rr-coder (production design), rr-review orchestration |
| rr-security-auditor | rr-coder CPNNN, full test coverage |
| rr-review | rr-ci POST mechanics, Omniva-specific MR scripts |

## Host-agnostic contract

- No `_oa-*` agent names in rrraw review path (v1: parent session + nested skill Read).
- No `.ai/review/` — use `.rr-builder/<runId>/`.
- No company Jira site assumptions — generic linked ticket/wiki URLs only ([rr-review/refs/brief-sources.md](../rr-review/refs/brief-sources.md)).
