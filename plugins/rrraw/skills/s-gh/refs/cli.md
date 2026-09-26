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
