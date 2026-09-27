# s-ci

Forge router for CI/ship. Detects GitHub vs GitLab and delegates apply to **s-gh** / **s-glab** (or **s-publish** / **s-deploy**). Human index only — runtime policy is [SKILL.md](SKILL.md).

## Why

One entry when forge is unknown; shared agent policy in `refs/ci/` without duplicating `gh`/`glab` apply rows in the router.

## What

Owns **detect-remote**, task-shape classification, and delegation. Shared policy (shapes, PR/MR templates, pipeline fix, Sonar fix, pull-dependabot, review triage) lives in `refs/ci/**`. Apply (CLI, forge flags, ship upsert) lives in forge skills.

**Out of scope:** forge CLI syntax, title/load/execute detail (delegate), local-only git → **s-git**.

## When

### Use when

- Forge unknown — `/s-ci` with any ship/fix/issue/CI shape
- Same routes as forge-direct entry: `--create-pr` / `--create-mr` / …, `--draft`, `--fix`, `--fix --sonar`, `--pull-dependabot`, issue, publish, deploy

### Avoid when

- GitHub-only and forge known → **s-gh**; GitLab-only → **s-glab**
- Local git without PR/MR → **s-git**

## Constraints

- **Policy:** `refs/ci/`
- **CLI:** [scripts/README.md](scripts/README.md), [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md)
- **Disk:** sidecars under **`.ai/ci/`**

## Notes

```
s-ci/
├── SKILL.md
├── scripts/
skills/s-gh/     # GitHub apply
skills/s-glab/   # GitLab apply
refs/ci/         # shared forge-agnostic policy
```
