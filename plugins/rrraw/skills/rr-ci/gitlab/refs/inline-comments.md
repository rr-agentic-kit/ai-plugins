# Inline MR comments (diff threads)

Code-level feedback must be an **inline** thread on the diff, not `glab mr note`, unless the user asked for a general comment.

## `new_line` must be a `+` line

GitLab `position.new_line` must appear as an **addition** in `GET .../merge_requests/:iid/changes` for that file. Context lines between hunks are invalid anchors (400 or a broken thread).

Before each inline comment:

1. Load `diff_refs` (`base_sha` / `start_sha` / `head_sha`).
2. Parse that file’s unified `diff`; collect new-file line numbers on `+` lines.
3. If the intended line is not in the set, anchor the nearest `+` line and name the real range in the body.

## Reviewer list

Append the current user (`--reviewer +@me` or MCP `reviewer_ids` plus `whoami().id`). Do not replace the list.

## Review instructions note

After posting ≥1 inline thread, `mr-ensure-review-instructions` may post one general note with marker `<!-- rr-ci:review-instructions -->` (idempotent). Then `mr-review-submit`.
