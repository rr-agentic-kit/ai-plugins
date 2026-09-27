# s-gh

GitHub apply skill — peer entry with **s-ci** / **s-glab**. Direct `/s-gh` when forge is GitHub; or loaded by **s-ci** after `detect-remote`. Runtime: [SKILL.md](SKILL.md).

## Why

GitHub-only `gh`/MCP and Actions patterns live here; shared ship/fix policy lives in `refs/ci/`.

## What

Routes PR upsert, Actions debug, bounded run wait (`scripts/wait-run.py`), review threads, pipeline fix apply rows, Sonar fix, security/quality reports, and pre-merge checks.

**Out of scope:** GitLab, local-only git, publish/deploy (siblings), inventing unlisted CLI.

## When

### Use when

- GitHub remote and PR/issue/Actions/review/fix/ship task
- Same invoke shapes as **s-ci** (ship routes, `--draft`, `--fix`, `--fix --sonar`, `--pull-dependabot`)

### Avoid when

- GitLab → **s-glab**; forge unknown → **s-ci**; local git → **s-git**

## Constraints

- **Policy:** `refs/ci/`
- **CLI:** parent `skills/s-ci/scripts/`, [SCRIPTS-SPEC.md](../s-ci/SCRIPTS-SPEC.md)
- Inline comments: [refs/inline-comments.md](refs/inline-comments.md)

## Notes

```
s-gh/
├── SKILL.md
├── scripts/   # wait-run.py, open-review-threads.sh
└── refs/      # cli, inline-comments, mcp, workflow-rules
refs/ci/       # shared forge-agnostic policy
```
