# rr-ci

Forge router + generic CI/ship. Nested GitLab/GitHub/publish/deployment skills are loaded by path; they are not plugin-listed.

Runtime: [SKILL.md](SKILL.md). CLI: [scripts/README.md](scripts/README.md), [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md).

## Goals

Detect GitHub vs GitLab, author PR/MR title/description, run pipeline/review helpers, then load forge or publish/deploy refs. Ship path may commit/push.

## Scope/limits

**In:** generic CI, dual `gh`/`glab` CLI (no Renovate). **Out:** company catalogs, required Jira keys, Omniva clusters.

## Audience

Agent runtime. Nested skills: `disable-model-invocation`.

## When to use

PR/MR, CI debug, publish, deploy. Local-only git → rr-git. Implement/review code → rr-builder.

## File structure

```
rr-ci/
├── SKILL.md                 # router
├── gitlab/SKILL.md          # GitLab
├── github/SKILL.md          # GitHub
├── publish/SKILL.md
├── deployment/SKILL.md
├── refs/                    # generic
└── scripts/                 # rr-ci CLI
```
