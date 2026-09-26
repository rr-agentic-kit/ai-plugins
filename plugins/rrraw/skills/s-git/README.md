# s-git

Local git specialist: safety, worktrees, squash, conflict resolution, merged-branch cleanup. Human index only — runtime policy is [SKILL.md](SKILL.md).

## Why

Agents mutate local git history and worktrees without silent `--force`, accidental `clean -fd`, or orphaned worktrees — while deferring PR/MR ship to s-ci.

## What

Owns repo-root resolution, destructive-git safety, worktree lifecycle, local squash onto base, merged local branch cleanup, conflict-resolution routing, and version-field conflict auto-resolve (latest semver).

**Out of scope:** PR/MR create/update, forge APIs, pipeline debug, publish/deploy (→ s-ci); implement/review code (→ rr-builder).

## When

### Use when

- Local commits, rebase, stash, amend, reflog recovery
- Worktrees, merge conflicts (incl. version-field auto-resolve), local squash, merged local branch cleanup
- Any `git` mutation when **not** opening or updating a PR/MR

### Avoid when

- Intent is open/update PR/MR, CI YAML, publish, or deploy → `s-ci`
- Implement, refactor, tests, security audit, or local code review → `rr-builder`

## Philosophy

- Confirm before history rewrite or discarding uncommitted work
- Local history only — forge PR/MR ship belongs to s-ci
- Prefer indexed helper CLIs over reinvented shell chains
- Eval-first: fix FAIL audit ids; preserve local-git specialist outcome
- Quiet finish commits — no full status or hook-stream dumps into context

## UX

### Invoke

Ambient match on local git / worktree / conflict / squash / clean-merged tasks; not for PR/MR ship.

### Intake

Resolve `REPO_ROOT` first; load one task ref from the SKILL table.

### Clarify

Load-ref fallback and dirty-tree clean options: Prefer AskQuestion; text-mode same options; no stall. Confirm before destructive discard/rewrite.

### Output

Command finished or user declined; helper stdout is `key=value` (see scripts README).

### Close

Stop on declined confirm, safety gate, or conflict finish Stop — do not continue into s-ci ship.

## Constraints

- **Safety:** Confirm before history rewrite or discarding work — [refs/safety.md](refs/safety.md)
- **Boundary:** Remote push only via loaded squash ref; never when intent is forge PR/MR → s-ci
- **Scripts:** Helper CLIs — [scripts/README.md](scripts/README.md)
- **Paths:** Plugin-root relative only
- **Eval-first:** Fix FAIL audit ids only; preserve local-git specialist outcome

## Notes

```
s-git/
├── SKILL.md
├── README.md
├── refs/
└── scripts/   # squash, clean, resolve_repo_root,
               # finish_commit_preflight, resolve_version_conflicts
```
