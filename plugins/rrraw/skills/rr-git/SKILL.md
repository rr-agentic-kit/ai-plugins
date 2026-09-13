---
name: rr-git
description: Local git safety, worktrees, rebase, squash, conflicts, merged local branch cleanup. Use for local commits/history — not PR/MR create (rr-ci owns ship).
---

# rr-git

**Human overview:** [README.md](README.md)

**Scripts:** helper CLIs — [scripts/README.md](scripts/README.md).

## Purpose

Steer **local** git operations and which ref to load. Do not replace upstream Git documentation. Destructive commands follow [refs/safety.md](refs/safety.md).

**Boundary:** Local commits and pre-PR history rewrite live here. Remote push only via a loaded squash ref — never when intent is open/update PR/MR → **rr-ci**. Force-push in the squash ref is still pre-forge squash (rr-git).

## When to use

- Branches, rebase, stash, amend, reflog recovery
- Worktrees for isolated worker steps
- Merge-conflict resolution
- Squash onto a base branch (local / pre-forge)
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

| Task | Read |
|------|------|
| Risk, force-push, recovery | [refs/safety.md](refs/safety.md) |
| Delegated worktrees | [refs/worktree-lifecycle.md](refs/worktree-lifecycle.md) |
| Local squash onto base (forge without native squash-on-merge) | [refs/squash-before-merge.md](refs/squash-before-merge.md) |
| Delete merged local branches | [refs/clean-local-branches.md](refs/clean-local-branches.md) |
| Merge conflicts | [refs/conflict-resolution.md](refs/conflict-resolution.md) |

**Fallback (no matching row):** AskQuestion to classify the task, or load [refs/safety.md](refs/safety.md) before any destructive git.

3. **execute** — Follow the ref. Confirm with the user before permanently discarding uncommitted work or rewriting history others may have pulled. Done: command finished or user declined. Stop: user declined confirm, or safety gate blocks.

## Invariants

- Destructive git risk/confirm rules: [refs/safety.md](refs/safety.md) — do not restate them here.
- Plugin paths are relative to the **rrraw** plugin root.

## Orchestration

Single-shot when one git command. Multi-step: TodoWrite ids above. No slash-command chaining.
