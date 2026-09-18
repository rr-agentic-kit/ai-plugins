# rr-builder routing

**Audience:** `rr-builder` skill after [input-resolution.md](input-resolution.md).

## Default routing table

| Input signal | Load |
|--------------|------|
| `--prepare`, prepare slice, decompose execute-slice, tech plan for slice | `rr-prepare/SKILL.md` |
| Implement, refactor, production code change | `rr-coder/SKILL.md` |
| Tests, coverage, flaky, migrate tests | `rr-tester/SKILL.md` |
| OWASP, secrets, vulnerability audit | `rr-security-auditor/SKILL.md` |
| `--code` / `--test` / `--security` / `--all` / review / `--fix` | `rr-review/SKILL.md` then lane skills as review directs |
| `--ci` / inline comments / pipeline after review | After review findings → `skills/rr-ci/SKILL.md` |
| Local worktree / destructive git during fix | `skills/rr-git/refs/` as rr-ci and rr-review already do |

## Review lane delegation

When `rr-review` runs assess:

| Lane | Nested skill |
|------|--------------|
| `code` | `rr-coder/SKILL.md` |
| `test` | `rr-tester/SKILL.md` |
| `security` | `rr-security-auditor/SKILL.md` |

Review orchestration (brief, chunk, Challenge, merge report) stays in **rr-review**; lane rubrics stay in nested skills.

## Plan-driven routing

When `payload.plan_path` is set (`docs/plans/` or user file) **or** an `execute-slice.yaml` / prepare intent is present:

1. Prepare / decompose / tech-plan-for-slice → **rr-prepare** (stop after L3; no auto-chain to coder).
2. Read plan goal and acceptance criteria.
3. Implementation tasks (already prepared or explicit implement) → **rr-coder**.
4. Test-only tasks → **rr-tester**.
5. Explicit security acceptance → **rr-security-auditor** or **rr-review** with `--security`.
6. "Review before merge" without lane → **rr-review** `--all`.

If the plan is planning-only (no code or prepare tasks), stop: **rr-planner** owns that artifact.

## Anti-patterns

- Loading all nested `SKILL.md` files in one turn.
- Auto-chaining **rr-prepare** → **rr-coder** in the same run.
- Running **rr-ci** before review completes when user only asked for local review.
- Using **rr-builder** for exec-summary / PRD authoring.
