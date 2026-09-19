# Git worktree lifecycle (workers)

**Purpose:** Git-only procedure for delegated workers. **Read** this file for every worktree / branch operation. Paths relative to the **target repo**, not the plugin.

## Placeholders

| Placeholder | Meaning |
|-------------|---------|
| `<repo>` | App repository root (main worktree) |
| `<base>` | Merge-target branch |
| `<N>` | Plan step number |
| `<phase>` | Worker label (e.g. `code-review`) |
| `<worktree_path>` | Repo-relative worktree directory |
| `<step_branch>` | Branch for the step |
| `<commit_message>` | Single-line commit message |

Use names from the Task prompt. Example: `.worktrees/step-<N>` and `fix-step-<N>`.

## When to use a worktree

If the Task says Fallback (single step, no parallel benefit), work only in the main worktree: do not `git worktree add`.

## Happy path (from `<repo>` unless noted)

1. `git worktree add <worktree_path> -b <step_branch> <base>`
2. Work with cwd = `<worktree_path>`; commit on `<step_branch>`.
3. Before merge: `git log <base>..HEAD` is **exactly one commit** unless the Task waives it. Squash with `git reset --soft <base>` then commit.
4. From `<repo>`: `git checkout <base>` then `git merge <step_branch>`.
5. `git worktree remove <worktree_path>` (`--force` last resort).
6. `git branch -d <step_branch>` (`-D` only after verifying the commit is on `<base>`).
7. Verify: `git worktree list` must not list `<worktree_path>`; branch gone.

## Failure path

If a worktree was created, still try remove + branch delete so the repo does not leak trees. Mention leftover branches in the error.

## Callback gate

Do not claim success until the worktree directory is gone and the step branch is deleted or explicitly kept.
