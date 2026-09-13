# Git safety

Risk gates for destructive local git. Recovery is reflog-first — not an encyclopedia of tutorials.

## Command risk matrix

| Command | Risk | Lose work? | Affects others? | Recoverable? |
|---------|------|------------|-----------------|--------------|
| `git push --force` | **CRITICAL** | Yes | Yes | Difficult |
| `git rebase` (pushed shared) | **CRITICAL** | Yes | Yes | Difficult |
| `git reset --hard` | **HIGH** | Uncommitted | No | No |
| `git clean -fd` | **HIGH** | Untracked | No | No |
| `git checkout -- .` | **HIGH** | Uncommitted | No | No |
| `git push --force-with-lease` | **MEDIUM** | Conditional | Yes | Difficult |
| `git branch -D` | **MEDIUM** | If unmerged | No | Reflog |
| `git commit --amend` (pushed) | **MEDIUM** | Conditional | Yes | Difficult |
| `git rebase` (local only) | **LOW** | No | No | Reflog |
| `git reset --soft` / `--mixed` | **LOW** | No | No | Yes |
| `git stash` / `merge` / `cherry-pick` | **LOW** | No | No | Yes |

## Force-with-lease rule

On shared remotes: **`git push --force-with-lease` only** — never `--force`. Lease fails if the remote moved; stop and reconcile. Prefer new commits or team coordination over rewrite on shared branches.

## Confirm gates

Ask the user before permanently discarding uncommitted work or rewriting history others may have pulled:

- `reset --hard`, `clean -fd`, `checkout -- .`
- Deleting **unmerged** branches (`branch -D`)
- Force-push / amend / rebase of **already-pushed** commits
- Squash script `--force-push` (see [squash-before-merge.md](squash-before-merge.md))

Pre-check: `git status`; stash or backup branch when unsure.

## Reflog

`git reflog` records HEAD moves (~90 days). Recovery pattern: find SHA → `git branch recovery <sha>` or `git reset --hard <sha>` (confirm first).

## rr-git scenarios

### Force-push mistake

Remote history diverged or teammates lost commits. Stop random resets. `git fetch`; recover lost tip via teammate/local reflog; merge both lines; push normally. Prefer `--force-with-lease` next time.

### Lost branch / commits

`git reflog` (or `git fsck --lost-found`) → recreate `git branch <name> <sha>`. Uncommitted work after `reset --hard` / `clean -fd` is usually **gone**.

### Secrets committed

If not pushed: remove secrets, `commit --amend`. If pushed: remove in a new commit, **rotate credentials immediately**; history rewrite only with team coordination (`git-filter-repo` / BFG).

## Related refs

| Workflow | Ref |
|----------|-----|
| Local squash onto base | [squash-before-merge.md](squash-before-merge.md) |
| Prune merged local branches | [clean-local-branches.md](clean-local-branches.md) |
