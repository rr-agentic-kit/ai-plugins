# gh CLI (syntax)

Official docs: [GitHub CLI](https://cli.github.com/manual/). This ref is flags agents actually need.

```bash
gh auth status
gh pr view
gh pr create --draft --fill --title "..." --body-file body.md
gh pr edit --title "..." --body-file body.md
gh pr checks
gh pr review --approve
gh pr review --request-changes --body "..."
gh run list --branch "$BRANCH" --limit 1
gh run view RUN_ID --log-failed
gh run rerun RUN_ID --failed
```

Prefer `gh` over raw `curl` to `api.github.com` when `gh` is authenticated. JSON: `gh … --json fields`.
