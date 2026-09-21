# glab syntax

Do not copy `glab --help` into context. Run `glab <command> --help` for flags.

## MR title and description

Parent skill `refs/pr-mr-templates.md`. Default create flags: nested SKILL **Default MR ship**.

```bash
glab mr create --draft --target-branch BASE --fill --yes --squash-before-merge --remove-source-branch -t "..." -d "..."
glab mr update -t "..." -d "..."
glab mr update --target-branch BASE
```

Default ship create always includes `--draft` and `--target-branch` from `mr-add-preflight` `result.base_branch`.

## Issues

```bash
glab issue create --repo OWNER/REPO -t "..." -d "..."
glab issue create -t "..." -d "..."
```

Use `--repo` when forge target ≠ cwd origin. Draft → approve → create: parent/nested **Issue create** steps — do not invent flags.

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
