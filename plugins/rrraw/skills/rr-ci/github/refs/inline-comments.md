# GitHub inline review comments

Post comments on a **line in the PR diff** (the equivalent of GitLab `+` lines). Do not use a general issue comment for line-specific findings unless the user asked for a summary comment.

- `path` = file in the PR.
- `line` / `side` = the line in the *new* file for additions/changes.
- Submit via `gh api` pull review comments or MCP review-comment tools.
- Do not comment on lines that are not part of the PR diff.
