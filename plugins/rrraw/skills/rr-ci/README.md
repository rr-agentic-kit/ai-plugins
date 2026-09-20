# rr-ci

Forge router + generic CI/ship. Nested GitLab/GitHub/publish/deployment skills are loaded by path; they are not plugin-listed. Human index only — runtime policy is [SKILL.md](SKILL.md).

## Why

One forge-agnostic ship path: detect GitHub vs GitLab, author PR/MR title/description, draft/create tracker issues (including cross-repo), debug pipelines, then load the right nested skill — without duplicating forge-only facts in the root.

## What

Owns detect-remote, PR/MR templates, issue draft→approve→create routing, pipeline/review CLI helpers, and routing into nested forge / publish / deployment skills. Ship path may commit/push when creating or updating a PR/MR. Forge **target** may differ from cwd origin when the user names `owner/repo`.

**Out of scope:** employer/internal cluster catalogs, required tracker keys in titles, Renovate onboarding CLI, local-only git (→ rr-git), implement/review code (→ rr-builder), inventing unlisted `gh`/`glab` flags, treating `--create-*` / `--update-*` as JSON-CLI subcommands (those are skill invoke routes only).

## When

### Use when

- Opening or updating a PR/MR (including commit/push for that flow)
- Named routes: `--create-pr` / `--create-mr` / `--update-pr` / `--update-mr` (or `--create-pr-mr` / `--update-pr-mr`) — all mean upsert; combine with `--draft` to gate title/body on disk
- Drafting or creating a GitHub/GitLab issue (same or other `owner/repo`)
- Pipeline / Actions failure, CI reports, review submit, pending reviews
- Publishing artifacts or deploying via Helm/K8s/GitOps

### Avoid when

- Local git only (rebase, worktree, conflicts, merged branch cleanup) with no PR/MR → `rr-git`
- Implement, refactor, tests, or multi-lane code review → `rr-builder`
- Employer/internal catalogs (pinned versions, cluster inventories, required tracker keys)

## Philosophy

- Eval-first: thicken from FAIL or live miss, not anticipated edges
- Forge-only facts live in nested skills — root stays agnostic
- Named ship routes are invoke/task-shape aliases for one upsert path — not invent JSON-CLI commands
- Happy-path upsert stays turn-cheap (batch loads; conditional safety)

## UX

### Invoke

Slash `/rr-ci` with `--create-pr` / `--create-mr` / `--update-pr` / `--update-mr` (or `-pr-mr` aliases) — same upsert ship; optional `--draft` writes `.ai/ci/pr-mr-title.txt` + `.ai/ci/pr-mr-body.md` and AskQuestions next steps. Nested forge skills are path-loaded only.

### Intake

Need repo root + forge remote; optional `owner/repo` when not cwd origin.

### Clarify

Enumerable forks (forge unknown, task-shape, forge target, `--draft` Ship|Keep|Edit, issue draft approve): AskQuestion preferred; same options as short prose if the tool is unavailable.

### Output

PR/MR or issue URL; pipeline/debug envelopes from CLI when that was the ask.

### Close

After issue create or PR/MR ship: report URL; do not invent follow-on forge commands outside the skill.

## Constraints

- **Invoke:** Nested skills are `disable-model-invocation`; load by path from this skill only
- **CLI:** JSON envelope — [scripts/README.md](scripts/README.md), frozen surface [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md); issue create uses allowlisted `gh`/`glab` in nested forge skills
- **Disk:** Sidecar files under **`.ai/ci/`** only (e.g. `debug-pipeline --save-log` → `.ai/ci/job-<id>.log`; `--draft` ship → `pr-mr-title.txt` / `pr-mr-body.md`)
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
