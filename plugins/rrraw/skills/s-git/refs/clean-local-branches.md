# Clean merged local branches

**When:** Delete local branches already merged into `origin/master` or `origin/main`. Not `git clean` (untracked files) — see [safety.md](safety.md).

**Script:** `skills/s-git/scripts/clean-merged-local-branches.sh` — invoke from [scripts/README.md](../scripts/README.md). Requires a clean worktree for `--plan`/`--delete` unless the user picks a dirty-tree option below.

## Script flags

`--worktree-status` | `--plan` | `--delete`; `--base <name>`; `--checkout-base`; `--skip-validation` (manual testing only).

## Dirty worktree

1. Run `--worktree-status`. Parse `dirty`, `start_branch`, `base`, `start_merged`.
2. If `dirty=no` → run `--plan` then `--delete` (after confirm) without loading extra policy.
3. If `dirty=yes` and `start_merged=yes` → AskQuestion: abort; stash then delete; discard then delete (text-mode same options; no stall).
4. If `dirty=yes` and `start_merged=no` → stash, run script, checkout `start_branch`, stash pop.
