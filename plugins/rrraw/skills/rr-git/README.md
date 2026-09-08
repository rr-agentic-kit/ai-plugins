# rr-git

Local git specialist: safety, worktrees, squash, conflict resolution, merged-branch cleanup. Runtime policy is [SKILL.md](SKILL.md).

## Goals

Agents mutate git history and worktrees without silent `--force`, accidental `clean -fd`, or orphaned worktrees.

## Scope/limits

**In:** local git. **Out:** PR/MR create (rr-ci), forge APIs, implement/review code (rr-builder).

## Audience

Agent runtime. Humans: this README.

## When to use

See SKILL.md. Do not load for “open a PR” alone.

## File structure

```
rr-git/
├── SKILL.md
├── README.md
├── refs/
└── scripts/          # clean-merged-local-branches.sh, squash-onto-base.sh
```
