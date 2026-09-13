# Clean merged local branches

**When:** Delete local branches already merged into `origin/master` or `origin/main`. Not `git clean` (untracked files) — see [safety.md](safety.md).

**Script:** `skills/rr-git/scripts/clean-merged-local-branches.sh` — invoke from [scripts/README.md](../scripts/README.md) (`--plan` then `--delete`). Requires a clean worktree unless the user picks a dirty-tree option below.

## Script flags

`--plan` | `--delete`; `--base <name>`; `--checkout-base`; `--skip-validation` (manual testing only).

## Dirty worktree

Record `START_BRANCH`. Detect `$BASE` (`master` if `origin/master` exists, else `main`).

| Start branch merged into `origin/$BASE`? | Action |
|------------------------------------------|--------|
| Yes + dirty | AskQuestion: abort; stash then delete; discard then delete |
| No + dirty | Stash, run script, checkout `START_BRANCH`, stash pop |

On a clean tree, run the script without loading extra policy.
