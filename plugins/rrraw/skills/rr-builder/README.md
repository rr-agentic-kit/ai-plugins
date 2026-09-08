# rr-builder

Router skill for **building and reviewing code** in generic repos. One human-invocable entry point; nested lanes load on demand.

## Goals

Classify implement, test, security, or review work from flags/plan/NL and load exactly one nested skill per turn. Review artifacts land under **`.rr-builder/<runId>/`**.

## Scope / limits

- Does not run cascade planning (**rr-planner**), PR/MR forge POST (**rr-ci** except `--ci` handoff), or local git ops (**rr-git**)
- Nested skills are path-loaded only — not listed in `plugin.json`
- Does not preload every nested skill on one prompt

## Audience

Developers and agents invoking **rr-builder** for code, tests, security audit, or multi-lane review. Not for product planning docs or CI ship mechanics alone.

## When to use

- Implement/refactor production code, test flows (`--assess`, `--write-tests`, …), OWASP audit, or review (`--code`, `--test`, `--security`, `--all`, `--fix`, `--ci`)

## Lanes

| Lane | Nested skill | Typical input |
|------|--------------|---------------|
| Implement / refactor | `rr-coder/` | Plan task, "implement X", refactor request |
| Tests | `rr-tester/` | `--assess`, `--write-tests`, `--complete-missing-tests`, … |
| Security | `rr-security-auditor/` | OWASP audit, secrets scan, pre-ship security |
| Review | `rr-review/` | `--code`, `--test`, `--security`, `--all`, `--fix`, `--ci` |

## Quick start

```
rr-builder implement the auth module from docs/plans/prd.md
rr-builder --assess --scope diff
rr-builder --security --scope diff
rr-builder --all --scope MR
rr-builder --all --fix --scope diff
rr-builder --all --ci --scope MR
```

Former `rr-test` flags work when you **`Read`** `rr-tester/SKILL.md` via this router or invoke `rr-builder` with test flags ([refs/input-resolution.md](refs/input-resolution.md)).

## Not in scope

- **rr-planner** — product/planning docs only
- **rr-ci** — PR/MR, pipelines, forge POST (review `--ci` hands off here)
- **rr-git** — local git safety and worktrees

## Layout

```
rr-builder/
  SKILL.md          # router (plugin-listed)
  refs/             # input + routing + anti-overlap
  rr-coder/         # production code standards
  rr-tester/        # test excellence (moved from rr-test)
  rr-security-auditor/
  rr-review/        # multi-lane review hub → .rr-builder/<runId>/
```

Review artifacts: **`.rr-builder/<runId>/`** at repo root (see `rr-review/refs/artifacts.md`).

## Audit note

Nested lane skills (`rr-coder/`, `rr-tester/`, `rr-security-auditor/`, `rr-review/`) intentionally fail context-engineer `static.name.path-match` — they are path-loaded children of `rr-builder`, not top-level `skills/<name>/` entries.
