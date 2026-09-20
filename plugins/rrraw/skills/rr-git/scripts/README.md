# rr-git helper scripts

Bash/Python helpers for local squash, merged-branch cleanup, repo-root resolve, finish-commit preflight, and version-conflict auto-resolve. Invoke from the **target git repo** (cwd = repo root) unless `--repo` / `--candidate` is passed. Paths below are relative to the **rrraw plugin root**.

## Invoke

```bash
# Repo root resolve/validate
python3 skills/rr-git/scripts/resolve_repo_root.py
python3 skills/rr-git/scripts/resolve_repo_root.py --candidate <path>

# Finish-commit preflight (merge/rebase)
python3 skills/rr-git/scripts/finish_commit_preflight.py
python3 skills/rr-git/scripts/finish_commit_preflight.py --repo <path>

# Squash onto base
bash skills/rr-git/scripts/squash-onto-base.sh --verify-only [<source-branch>]
bash skills/rr-git/scripts/squash-onto-base.sh --force-push [<source-branch>]

# Clean merged local branches
bash skills/rr-git/scripts/clean-merged-local-branches.sh --worktree-status
bash skills/rr-git/scripts/clean-merged-local-branches.sh --plan
bash skills/rr-git/scripts/clean-merged-local-branches.sh --delete

# Version-field merge conflicts (latest semver)
python3 skills/rr-git/scripts/resolve_version_conflicts.py --plan
python3 skills/rr-git/scripts/resolve_version_conflicts.py --apply
```

Policy gates and when-to-run: [refs/squash-before-merge.md](../refs/squash-before-merge.md), [refs/clean-local-branches.md](../refs/clean-local-branches.md), [refs/conflict-resolution.md](../refs/conflict-resolution.md), [refs/repo-root.md](../refs/repo-root.md), [refs/safety.md](../refs/safety.md).

## resolve_repo_root.py

| Flag | Meaning |
|------|---------|
| (none) | Emit cwd git toplevel |
| `--candidate <path>` | Validate user-supplied path is the work-tree root |

**Stdout:** `status=ok|error`, `repo_root` (ok), or `error`/`message`/`remediation`. **Exit:** `0` ok; `1` error.

## finish_commit_preflight.py

| Flag | Meaning |
|------|---------|
| `--repo <path>` | Git repo root (default: cwd) |
| `--warn-threshold <n>` | Warn when hooks likely and staged count ≥ n (default: 50) |

**Stdout:** `status=ok|error`, `staged_count`, `hooks_likely=yes|no`, `warn=yes|no`, `warn_threshold`. **Exit:** `0` ok; `1` error.

## squash-onto-base.sh

| Mode / flag | Meaning |
|-------------|---------|
| `--verify-only` | Clone, squash, tree-check; print summary; do not push |
| `--force-push` | Same checks, then force-with-lease after confirm; sync caller repo |
| `[<source-branch>]` | Defaults to current branch |
| `--yes` | Skip force-push confirmation |
| `--auto-cleanup` / `--no-cleanup` | Temp clone cleanup |
| `--integrate rebase\|none` | Rebase onto origin base before squash (default: none) |
| `--base <branch>` | Override base (else auto master→main) |

Env: `BASE_BRANCH`, `OUTPUT_BRANCH`, `COMMIT_MSG`, `COMMIT_SUBJECT`.

**Stdout:** `key=value` status block (`status=…`, optional `error`/`message`/`remediation`, tree SHAs). **Exit:** `0` success; non-zero on failure or skip (e.g. GitLab host skip).

## clean-merged-local-branches.sh

| Flag | Meaning |
|------|---------|
| `--worktree-status` | Emit `dirty` / `start_branch` / `base` / `start_merged` (allows dirty) |
| `--plan` | Classify only; print candidates |
| `--delete` | Classify then delete confirmed merged locals |
| `--base <name>` | Override base (default: auto master→main) |
| `--checkout-base` | When clean and HEAD ≠ base, checkout base before sync |
| `--skip-validation` | Skip pre-flight/pull (manual testing only) |

`--plan`/`--delete` require a clean worktree unless dirty-tree orchestration in the clean ref applies. **Stdout:** status/`key=value` classification. **Exit:** `0` success; `1` error.

## resolve_version_conflicts.py

Auto-resolve **version** fields in unmerged conflict hunks — **latest semver wins**. Field-scoped; never whole-file ours/theirs. Allowed paths: `*/.cursor-plugin/plugin.json`, `*/.claude-plugin/plugin.json`, `pyproject.toml`, `marketplace.json`.

| Flag | Meaning |
|------|---------|
| `--plan` | Print planned resolutions; do not write |
| `--apply` | Write version resolutions into the work tree |
| `--repo <path>` | Git repo root (default: cwd) |
| `--file <path>` | Limit to path (repeatable); default = all unmerged allowed paths |

**Stdout:** `key=value` (`status=ok|partial|error`, `resolved`, `remaining`, `files_applied` / `files_planned`, `files_remaining`, `files_skipped`). **Exit:** `0` clean or nothing to do; `1` error; `2` versions fixed but non-version conflicts remain (continue conflict-resolution workflow).
