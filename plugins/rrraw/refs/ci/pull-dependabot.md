# pull-dependabot

Batch-merge `origin/dependabot/**` into the current branch. **Apply row owns the loop;** the agent intervenes only on escalate. Mirror `--fix --sonar` token economy.

## When

Task-shape is `--pull-dependabot` / prose “merge Dependabot remotes”. Forge must be **GitHub** (Dependabot remotes). Do not use for Renovate onboarding or general dep edits.

## Procedure

1. **Preflight** — Clean working tree; forge must be GitHub (else stop: GitHub-only). Done: ready or stopped.
2. **Optional dry-run** — Run the apply row with dry-run once if the user wants a branch list. Paste ≤50 lines of JSON. Done.
3. **Run (one shell)** — Run the **pull-dependabot** apply row with a verify command (e.g. project test recipe). Do **not** chat-orchestrate per-branch merge/verify/delete. Progress is stderr; parse stdout JSON only. Done: envelope in context.
4. **Branch on `result.status` / exit**
   - `ok` / `empty` (exit 0) → report `summary` counts only. If user asked to ship → existing PR/MR **upsert** (ship shape); do not invent a second ship path.
   - `escalate` (exit 2) → load this section **Escalate** once; do not dump verify log bodies (point at `result.branches[].log` / `log_dir`).
   - `ok: false` / exit 1 → stop with `error.code`.
5. **Anti-triggers** — No per-branch TodoWrite loops; no inventing `git merge` chains when the apply row exists; no pasting full verify logs; no loading project-local Dependabot recipes as a substitute; no home-wide or plugin-cache walks to rediscover the command.

## Apply row missing / unwired

If the pull-dependabot apply row is unavailable:

1. **One check** — confirm the command is registered in s-ci CLI surface (forge skill or parent SCRIPTS-SPEC).
2. **If listed but unwired** — invoke once from the plugin scripts dir with the same flags; do not invent a parallel merge loop.
3. **If not listed** — stop; do not invent the feature. Report surface gap.
4. **Never** search `$HOME` / plugin caches for alternate installs.

## Escalate (exit 2)

On escalate, **batch** in one tool turn: conflict paths, both-side manifests for those paths, and the remaining `branches[]` / skipped remotes. Then act:

| `merge` / signal | Agent action |
|------------------|--------------|
| `conflicts` + only unresolved non-lock paths | Resolve under safe union (manifest non-overlap) or AskQuestion; finish merge commit; re-run apply row for **remaining** remotes (or continue-on-fail next time) |
| `conflicts` + **layout / structural mismatch** (Dependabot target path or root manifest shape no longer matches the workspace — e.g. pre-workspace root `package.json` vs workspace package manifests) | **Abort** the merge (`git merge --abort`). Compare remote bump targets to **current** workspace manifests. If bumps are already present at equal/newer → treat remotes as **obsolete**; AskQuestion: **Close stale Dependabot PRs** \| **Leave open**. Do **not** force-resolve obsolete manifests into HEAD. |
| `verify_failed` | Inspect `log` path on disk (≤80 lines of failing step); fix tree; commit fix; re-run verify; then delete remote branch if appropriate |
| lockfile-only | Apply row already attempts regen; if still escalating, treat as verify/conflict above |

After resolving one escalate, prefer **re-invoking** the apply row for leftovers over inventing a parallel loop.

## Stop

- Dirty tree / missing verify command → fatal.
- Non-GitHub forge → stop before apply row (skill gate).
- Unresolved markers left in tree → fatal; do not ship.
- Renovate onboarding → out of scope.
- **Do not invent** `dependabot.yml` directory / ecosystem rewrites as a follow-up. If the user explicitly asks: for a **pnpm workspace with shared root lockfile**, keep `directory: /` only — never point Dependabot at workspace package subdirs (e.g. `/front`) for that lockfile layout.
