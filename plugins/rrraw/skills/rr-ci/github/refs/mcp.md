# GitHub MCP fallback

Use when `gh` is missing. Call MCP tools that map to PR view/create, check runs, and reviews. Do not invent GitLab MCP tool names.

- Resolve owner/repo from `git remote get-url origin`.
- Inline comments need a diff line on the PR head (see [inline-comments.md](inline-comments.md)).
- Pipeline logs: use the Actions/check-run tools if present; otherwise tell the user to install `gh`.
