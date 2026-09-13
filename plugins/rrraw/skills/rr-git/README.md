# rr-git

Local git specialist: safety, worktrees, squash, conflict resolution, merged-branch cleanup. Human index only — runtime policy is [SKILL.md](SKILL.md).

## Why

Agents mutate local git history and worktrees without silent `--force`, accidental `clean -fd`, or orphaned worktrees — while deferring PR/MR ship to rr-ci.

## What

Owns repo-root resolution, destructive-git safety, worktree lifecycle, local squash onto base, merged local branch cleanup, and conflict-resolution routing.

**Out of scope:** PR/MR create/update, forge APIs, pipeline debug, publish/deploy (→ rr-ci); implement/review code (→ rr-builder).

## When

### Use when

- Local commits, rebase, stash, amend, reflog recovery
- Worktrees, merge conflicts, local squash, merged local branch cleanup
- Any `git` mutation when **not** opening or updating a PR/MR

### Avoid when

- Intent is open/update PR/MR, CI YAML, publish, or deploy → `rr-ci`
- Implement, refactor, tests, security audit, or local code review → `rr-builder`

## Constraints

- **Safety:** Confirm before history rewrite or discarding work — [refs/safety.md](refs/safety.md)
- **Boundary:** Remote push only via loaded squash ref; never when intent is forge PR/MR → rr-ci
- **Scripts:** Helper CLIs — [scripts/README.md](scripts/README.md)
- **Paths:** Plugin-root relative only
- **Eval-first:** Fix FAIL audit ids only; preserve local-git specialist outcome

## Notes

```
rr-git/
├── SKILL.md
├── README.md
├── refs/
└── scripts/   # squash-onto-base.sh, clean-merged-local-branches.sh
```
