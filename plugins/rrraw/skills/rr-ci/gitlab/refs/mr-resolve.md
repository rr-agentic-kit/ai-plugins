# Resolve open merge request

Use when a flow must POST inline comments or needs a linked **open** MR.

Prefer CLI: `rr-ci mr-ci-review-preflight [mr_ref]`.

## Prerequisites

- `REPO_ROOT` per rr-git `refs/repo-root.md`
- `glab` authenticated; cwd = `REPO_ROOT`
- Only `state=opened` MRs. Merged/closed → stop.

## Inputs

| Input | Meaning |
|-------|---------|
| `mr_ref` (optional) | GitLab MR URL, `!IID`, or numeric IID |
| (none) | Open MR for the current source branch |

If none found → stop. Do not create an MR from this ref.
