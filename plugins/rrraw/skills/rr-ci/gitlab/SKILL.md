---
name: gitlab
disable-model-invocation: true
description: GitLab-specific MR, pipeline, glab/MCP, and .gitlab-ci.yml patterns. Loaded by rr-ci after detect-remote returns gitlab — not listed as a top-level plugin skill.
---

# rr-ci / GitLab

Loaded only from parent **rr-ci** `SKILL.md` when `result.forge` is `gitlab`.

## Purpose

Route GitLab MR, pipeline, discussion, and CI report work through **glab** (if installed) or **GitLab MCP**. Generic title/description rules stay in parent `refs/pr-mr-templates.md`.

## When to use

Parent **rr-ci** already selected GitLab. Do not load for GitHub remotes.

## When not to use

- GitHub PRs / Actions → sibling **github** skill
- Local git without an MR → **rr-git**
- Helm/K8s/Argo deploy mechanics → sibling **deployment** skill
- Pages/registry publish → sibling **publish** skill

## Procedure

1. **Tool** — `which glab`; if missing, [refs/mcp.md](refs/mcp.md). Done: glab or MCP.
2. **CLI** — From target repo: `uv run --project <rrraw-plugin>/skills/rr-ci/scripts rr-ci <command>` (parent `scripts/README.md`). Done: envelope parsed.
3. **Task row** — Read only the matching ref:

| Task | Read / run |
|------|------------|
| glab syntax | [refs/cli.md](refs/cli.md) |
| Inline MR threads | [refs/inline-comments.md](refs/inline-comments.md) |
| Resolve open MR | [refs/mr-resolve.md](refs/mr-resolve.md) |
| Failed pipeline | `debug-pipeline` `[MR_IID]` — branch on `result.status`, `result.error_lines`, `result.failed_job_id` |
| CI code-quality | `code-quality-reports` — `result.reports.count`, `result.reports.nodes` |
| Pipeline security | `pipeline-security-reports` — `result.merge_blocked`, `result.findings.*` |
| Bulk resolve threads | `mr-skip-threads` |
| MR add preflight | `mr-add-preflight` |
| Review instructions note | `mr-ensure-review-instructions` |
| Review decision | `mr-review-submit` |
| Pending reviews | `pending-reviews` |
| `rules:` / artifact paths | [refs/pipeline-rules.md](refs/pipeline-rules.md) |
| Code-quality when-to-use | [refs/code-quality-reports.md](refs/code-quality-reports.md) |
| Security reports when-to-use | [refs/pipeline-security-reports.md](refs/pipeline-security-reports.md) |
| MCP fallback | [refs/mcp.md](refs/mcp.md) |

4. **Default MR create** (after preflight `ready_create`): `glab mr create --fill --yes --draft --squash-before-merge --remove-source-branch` unless the user asked otherwise. Title/description from parent templates.
5. **Pre-merge** (when asked) — stop at first failure:

1. `glab mr view` — pipeline, approvals, conflicts  
2. Pipeline success (else `debug-pipeline`)  
3. `pipeline-security-reports` — `merge_blocked`  
4. Unresolved threads  
5. Required approvals  

**Pre-merge report:** Pipeline, security, discussions, approvals, merge ready/blocked, one-line verdict.

## Invariants

- After pipeline fixes: commit/push allowed (parent rr-ci); retry with `glab ci retry JOB_ID`.
- Do not invent `rr-ci` subcommands — parent `SCRIPTS-SPEC.md`.
- Inline comments: `new_line` must be a `+` line ([refs/inline-comments.md](refs/inline-comments.md)).
