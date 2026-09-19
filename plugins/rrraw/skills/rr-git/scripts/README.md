# rr-git helper scripts

Bash helpers for local squash and merged-branch cleanup. Invoke from the **target git repo** (cwd = repo root). Paths are relative to the **rrraw plugin root**.

## Invoke

```bash
# Squash onto base
bash skills/rr-git/scripts/squash-onto-base.sh --verify-only [<source-branch>]
bash skills/rr-git/scripts/squash-onto-base.sh --force-push [<source-branch>]

# Clean merged local branches
bash skills/rr-git/scripts/clean-merged-local-branches.sh --plan
bash skills/rr-git/scripts/clean-merged-local-branches.sh --delete
```

Policy gates and when-to-run: [refs/squash-before-merge.md](../refs/squash-before-merge.md), [refs/clean-local-branches.md](../refs/clean-local-branches.md), [refs/safety.md](../refs/safety.md).

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
| `--plan` | Classify only; print candidates |
| `--delete` | Classify then delete confirmed merged locals |
| `--base <name>` | Override base (default: auto master→main) |
| `--checkout-base` | When clean and HEAD ≠ base, checkout base before sync |
| `--skip-validation` | Skip pre-flight/pull (manual testing only) |

Requires a clean worktree unless dirty-tree orchestration in the clean ref applies. **Stdout:** status/`key=value` classification. **Exit:** `0` success; `1` error.
