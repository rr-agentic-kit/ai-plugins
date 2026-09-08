---
name: github
disable-model-invocation: true
description: GitHub-specific PR, Actions, and gh/MCP patterns. Loaded by rr-ci after detect-remote returns github — not listed as a top-level plugin skill.
---

# rr-ci / GitHub

Loaded only from parent **rr-ci** `SKILL.md` when `result.forge` is `github`.

## Purpose

Route GitHub PR, Actions, review, and check-run work through **gh** (if installed) or GitHub MCP. Generic title/description rules stay in parent `refs/pr-mr-templates.md`.

## When to use

Parent **rr-ci** already selected GitHub. Do not load for GitLab remotes.

## When not to use

- GitLab MRs / `glab` → sibling **gitlab** skill
- Local git without a PR → **rr-git**
- Helm/K8s/Argo → sibling **deployment** skill
- Pages/releases/packages → sibling **publish** skill

## Procedure

1. **Tool** — `which gh`; if missing, [refs/mcp.md](refs/mcp.md). Done: gh or MCP.
2. **CLI** — `uv run --project <rrraw-plugin>/skills/rr-ci/scripts rr-ci <command>` (parent `scripts/README.md`). Same command names as GitLab; GitHub backend maps them. Done: envelope parsed.
3. **Task row:**

| Task | Read / run |
|------|------------|
| gh syntax | [refs/cli.md](refs/cli.md) |
| Review comments on diff lines | [refs/inline-comments.md](refs/inline-comments.md) |
| Failed Actions run | `debug-pipeline` `[PR_NUMBER]` — `result.status`, `result.error_lines`, `result.failed_job_id` (check-run / job id) |
| Code scanning / quality | `code-quality-reports` |
| Security / Dependabot / code scanning | `pipeline-security-reports` — treat `merge_blocked` as merge-state dirty when GitHub reports failing required checks |
| Resolve review threads | `mr-skip-threads` |
| PR add preflight | `mr-add-preflight` |
| Review body note | `mr-ensure-review-instructions` |
| Review decision | `mr-review-submit` (`gh pr review`) |
| Pending reviews | `pending-reviews` |
| Workflow `if:` / artifact paths | [refs/workflow-rules.md](refs/workflow-rules.md) |
| MCP fallback | [refs/mcp.md](refs/mcp.md) |

4. **Default PR create** (after preflight `ready_create`): `gh pr create --draft --fill` unless the user asked otherwise. Title/description from parent templates. Prefer `--squash` merge method when the repo default is squash.
5. **Pre-merge** (when asked) — stop at first failure:

1. `gh pr view` — checks, reviews, conflicts  
2. Required checks green (else `debug-pipeline`)  
3. `pipeline-security-reports`  
4. Unresolved review threads  
5. Required reviews  

**Pre-merge report:** Checks, security, discussions, reviews, mergeable, one-line verdict.

## Invariants

- After workflow fixes: commit/push allowed (parent rr-ci); re-run with `gh run rerun RUN_ID --failed`.
- Do not invent `rr-ci` subcommands — parent `SCRIPTS-SPEC.md`.
- Inline comments must target a line in the PR diff ([refs/inline-comments.md](refs/inline-comments.md)).
