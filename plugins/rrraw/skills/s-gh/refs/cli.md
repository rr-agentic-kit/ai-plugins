# gh CLI (syntax)

Official docs: [GitHub CLI](https://cli.github.com/manual/). This ref is flags agents actually need.

```bash
gh auth status
gh pr view
gh pr create --draft --base BASE --fill --title "..." --body-file .ai/ci/pr-mr-body.md
gh pr edit --title "..." --body-file .ai/ci/pr-mr-body.md
gh pr edit --base BASE
gh pr checks
gh pr review --approve
gh pr review --request-changes --body "..."
gh run list --branch "$BRANCH" --limit 1
gh run view RUN_ID --log-failed
gh run rerun RUN_ID --failed
gh issue create --repo OWNER/REPO --title "..." --body "..."
gh issue create --title "..." --body-file body.md
```

Default ship create always includes `--draft` and `--base` from `mr-add-preflight` `result.base_branch`. Prefer `gh` over raw `curl` to `api.github.com` when `gh` is authenticated. JSON: `gh … --json fields`. Use `--repo OWNER/REPO` when forge target ≠ cwd origin.

## Open review threads (`scripts/open-review-threads.sh`)

Plugin-relative path: `skills/s-gh/scripts/open-review-threads.sh`. Requires `gh` + `jq`.

**List** (unresolved threads only; stdout JSON array):

```bash
open-review-threads.sh [--owner OWNER] [--repo REPO] [--pr NUMBER]
```

- Owner and repo both omitted → `gh repo view --json nameWithOwner`.
- PR omitted → `gh pr view --repo OWNER/REPO --json number` for the current branch (no `--head`).
- Pass both `--owner` and `--repo`, or neither; a half pair exits **2**.
- No open PR exits **1**. Empty unresolved set is `[]`, exit **0**.
- Each object: `id` (GraphQL thread node id), `path`, `line`, `outdated`, `comments[]` with `author`, `body`. No `url`, no resolved threads. If the thread page hits 100 nodes, one truncation line on stderr (still exit **0**).

**Reply** (by global thread node id; owner/repo/PR not required):

```bash
open-review-threads.sh --reply THREAD_ID (--body TEXT | --body-file PATH)
```

Stdout: `{"thread_id","comment_id"}`. Does **not** call `resolveReviewThread` — false-positive threads stay open per parent triage.
