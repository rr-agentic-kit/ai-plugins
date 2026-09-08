---
name: rr-git
description: Local git safety, worktrees, rebase, squash, conflict resolution, and branch cleanup. Use for commits, history rewrite, worktrees, or git clean — not PR/MR create (rr-ci owns ship including commit/push).
---

# rr-git

**Human overview:** [README.md](README.md)

## Purpose

Steer **local** git operations and which ref to load. Do not replace upstream Git documentation. Destructive commands follow [refs/safety.md](refs/safety.md).

## When to use

- Branches, rebase, stash, amend, reflog recovery
- Worktrees for isolated worker steps
- Merge-conflict resolution
- Squash onto a base branch (local)
- Delete merged **local** branches
- Any `git` mutation when **not** opening or updating a PR/MR

## When not to use

- Creating or updating a **PR/MR**, pipeline debug, reviews, CI YAML, publish, or deploy → **rr-ci** (that skill may commit/push as part of ship; still **Read** [refs/safety.md](refs/safety.md) before rewrite/force-push)
- Implement, refactor, tests, security audit, or local code review → **rr-builder**
- Forge-specific `gh` / `glab` API flows → nested **rr-ci/github** or **rr-ci/gitlab**

## Procedure

TodoWrite `merge: false` with ids `resolve-root`, `load-ref`, `execute` when the task has 3+ verifiable git steps; omit for a single command.

1. **resolve-root** — [refs/repo-root.md](refs/repo-root.md). Done: `REPO_ROOT` set; `git -C "$REPO_ROOT"`.
2. **load-ref** — Read the matching row below. Done: ref loaded.
3. **execute** — Follow the ref. Confirm with the user before permanently discarding uncommitted work or rewriting history others may have pulled. Done: command finished or user declined.

| Task | Read |
|------|------|
| Risk, force-push, recovery | [refs/safety.md](refs/safety.md) |
| Delegated worktrees | [refs/worktree-lifecycle.md](refs/worktree-lifecycle.md) |
| Bitbucket-style squash onto base | [refs/squash-before-merge.md](refs/squash-before-merge.md) |
| Delete merged local branches | [refs/clean-local-branches.md](refs/clean-local-branches.md) |
| Merge conflicts | [refs/conflict-resolution.md](refs/conflict-resolution.md) |

## Invariants

- `git push --force-with-lease`; never `--force` on shared remotes.
- Confirm before `reset --hard`, `clean -fd`, or deleting unmerged branches.
- Plugin paths are relative to the **rrraw** plugin root.

## Orchestration

Single-shot when one git command. Multi-step: TodoWrite ids above. No slash-command chaining.
