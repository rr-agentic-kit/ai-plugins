# s-glab

GitLab apply skill — peer entry with **s-ci** / **s-gh**. Direct `/s-glab` when forge is GitLab; or loaded by **s-ci** after `detect-remote`. Runtime: [SKILL.md](SKILL.md).

## Why

GitLab-only `glab`/MCP and `.gitlab-ci.yml` patterns live here; shared ship/fix policy lives in `refs/ci/`.

## What

Routes MR upsert, pipeline debug, inline threads, pipeline fix apply rows, Sonar fix, CI quality/security reports, and pre-merge checks.

**Out of scope:** GitHub, local-only git, publish/deploy (siblings), `--pull-dependabot` (GitHub only).

## When

### Use when

- GitLab remote and MR/issue/pipeline/review/fix/ship task
- Same invoke shapes as **s-ci** except `--pull-dependabot`

### Avoid when

- GitHub → **s-gh**; forge unknown → **s-ci**; local git → **s-git**

## Constraints

- **Policy:** `refs/ci/`
- **CLI:** parent `skills/s-ci/scripts/`, [SCRIPTS-SPEC.md](../s-ci/SCRIPTS-SPEC.md)
- Default MR ship flags: SKILL **Default MR ship**

## Notes

```
s-glab/
├── SKILL.md
└── refs/   # cli, inline-comments, mcp, pipeline-*, mr-resolve, …
refs/ci/    # shared forge-agnostic policy
```
