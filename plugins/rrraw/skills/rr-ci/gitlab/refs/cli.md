# glab syntax

Do not copy `glab --help` into context. Run `glab <command> --help` for flags.

## MR title and description

Parent skill `refs/pr-mr-templates.md`. Default create flags: this nested SKILL **Invariants**.

## Assignee and reviewer: append vs replace

`--assignee` and `--reviewer` prefix semantics (`glab mr update --help`):

- `+` — add
- `!` or `-` — remove
- (none) — **replace** the whole list

When posting review feedback, append the current user: `--reviewer +@me`.

## Notes vs inline threads

`glab mr note` is a general MR comment (no file/line). For diff-anchored threads, follow [inline-comments.md](inline-comments.md). Bulk resolve: `mr-skip-threads`.

## Failed jobs

Prefer `debug-pipeline` over hand-rolled `glab ci trace`. Retry: `glab ci retry JOB_ID`.
