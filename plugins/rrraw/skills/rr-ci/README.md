# rr-ci

Forge router + generic CI/ship. Nested GitLab/GitHub/publish/deployment skills are loaded by path; they are not plugin-listed. Human index only — runtime policy is [SKILL.md](SKILL.md).

## Why

One forge-agnostic ship path: detect GitHub vs GitLab, author PR/MR title/description, draft/create tracker issues (including cross-repo), debug pipelines, then load the right nested skill — without duplicating forge-only facts in the root.

## What

Owns detect-remote, PR/MR templates, issue draft→approve→create routing, pipeline/review CLI helpers, and routing into nested forge / publish / deployment skills. Ship path may commit/push when creating or updating a PR/MR. Forge **target** may differ from cwd origin when the user names `owner/repo`.

**Out of scope:** employer/internal cluster catalogs, required tracker keys in titles, Renovate onboarding CLI, local-only git (→ rr-git), implement/review code (→ rr-builder), inventing unlisted `gh`/`glab` flags.

## When

### Use when

- Opening or updating a PR/MR (including commit/push for that flow)
- Drafting or creating a GitHub/GitLab issue (same or other `owner/repo`)
- Pipeline / Actions failure, CI reports, review submit, pending reviews
- Publishing artifacts or deploying via Helm/K8s/GitOps

### Avoid when

- Local git only (rebase, worktree, conflicts, merged branch cleanup) with no PR/MR → `rr-git`
- Implement, refactor, tests, or multi-lane code review → `rr-builder`
- Employer/internal catalogs (pinned versions, cluster inventories, required tracker keys)

## UX

### Clarify

Enumerable forks (forge unknown, task-shape, forge target, issue draft approve): AskQuestion preferred; same options as short prose if the tool is unavailable.

### Close

After issue create or PR/MR ship: report URL; do not invent follow-on forge commands outside the skill.

## Constraints

- **Invoke:** Nested skills are `disable-model-invocation`; load by path from this skill only
- **CLI:** JSON envelope — [scripts/README.md](scripts/README.md), frozen surface [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md); issue create uses allowlisted `gh`/`glab` in nested forge skills
- **Disk:** Sidecar files under **`.ai/ci/`** only (e.g. `debug-pipeline --save-log` → `.ai/ci/job-<id>.log`)
- **Paths:** Plugin-root relative only — no `..` in skill/ref markdown
- **Eval-first:** Fix FAIL audit ids only when polishing; forge-issue expansion is a capability redesign (re-audit after absorb)

## Notes

```
rr-ci/
├── SKILL.md
├── github/SKILL.md
├── gitlab/SKILL.md
├── publish/SKILL.md
├── deployment/SKILL.md
├── refs/
└── scripts/
```
