# pull-dependabot

Batch-merge `origin/dependabot/**` into the current branch. **CLI owns the loop;** the agent intervenes only on escalate. Mirror `--fix --sonar` token economy.

**Invoke:** parent `scripts/README.md` → `pull-dependabot`. **Keys:** parent `SCRIPTS-SPEC.md`.

## When

Parent task-shape is `--pull-dependabot` / prose “merge Dependabot remotes”. Forge must be **GitHub** (Dependabot remotes). Do not use for Renovate onboarding or general dep edits.

## Procedure

1. **Preflight** — Clean working tree; `detect-remote` → `github` (else stop: GitHub-only). Done: ready or stopped.
2. **Optional dry-run** — `rr-ci pull-dependabot --dry-run` once if the user wants a branch list. Paste ≤50 lines of JSON. Done.
3. **Run (one shell)** — `rr-ci pull-dependabot --verify-cmd '<cmd>'` (e.g. `just test`). Do **not** chat-orchestrate per-branch merge/verify/delete. Progress is stderr; parse stdout JSON only. Done: envelope in context.
4. **Branch on `result.status` / exit**
   - `ok` / `empty` (exit 0) → report `summary` counts only. If user asked to ship → existing PR/MR **upsert** (steps title→load→execute); do not invent a second ship path.
   - `escalate` (exit 2) → load this section **Escalate** once; do not dump verify log bodies (point at `result.branches[].log` / `log_dir`).
   - `ok: false` / exit 1 → stop with `error.code`.
5. **Anti-triggers** — No per-branch TodoWrite loops; no inventing `git merge` chains when this command exists; no pasting full verify logs; no loading project-local Dependabot recipes as a substitute for this CLI; no home-wide or plugin-cache walks to rediscover the command.

## CLI missing / unwired

If `rr-ci pull-dependabot` returns invalid choice / unknown command:

1. **One check** — confirm command is listed in parent `SCRIPTS-SPEC.md` and registered in `scripts/cli.py` (`pull_dependabot.add_parser` + forge-agnostic).
2. **If listed but unwired** — invoke `pull_dependabot.main(...)` from the plugin `scripts/` dir once (same flags as the CLI); do not invent a parallel merge loop.
3. **If not listed** — stop; do not invent the feature. Report surface gap.
4. **Never** `find` across `$HOME` / `~/.claude/plugins/cache` for alternate installs.

## Escalate (exit 2)

On escalate, **batch** in one tool turn: conflict paths, both-side manifests for those paths, and the remaining `branches[]` / skipped remotes. Then act:

| `merge` / signal | Agent action |
|------------------|--------------|
| `conflicts` + only unresolved non-lock paths | Resolve under safe union (manifest non-overlap) or AskQuestion; finish merge commit; re-run CLI for **remaining** remotes (or `--continue-on-fail` next time) |
| `conflicts` + **layout / structural mismatch** (Dependabot target path or root manifest shape no longer matches the workspace — e.g. pre-workspace root `package.json` vs workspace package manifests) | **Abort** the merge (`git merge --abort`). Compare remote bump targets to **current** workspace manifests. If bumps are already present at equal/newer → treat remotes as **obsolete**; AskQuestion: **Close stale Dependabot PRs** \| **Leave open**. Do **not** force-resolve obsolete manifests into HEAD. |
| `verify_failed` | Inspect `log` path on disk (≤80 lines of failing step); fix tree; commit fix; re-run verify; then `git push origin --delete <branch>` if appropriate |
| lockfile-only | CLI already attempts regen; if still escalating, treat as verify/conflict above |

After resolving one escalate, prefer **re-invoking** `pull-dependabot` for leftovers over inventing a parallel loop.

## Stop

- Dirty tree / missing `--verify-cmd` → fatal (`dirty_tree` / `missing_verify_cmd`).
- Non-GitHub forge → stop before CLI (skill gate).
- Unresolved markers left in tree → fatal; do not ship.
- Renovate onboarding → out of scope.
- **Do not invent** `dependabot.yml` directory / ecosystem rewrites as a follow-up. If the user explicitly asks: for a **pnpm workspace with shared root lockfile**, keep `directory: /` only — never point Dependabot at workspace package subdirs (e.g. `/front`) for that lockfile layout.
