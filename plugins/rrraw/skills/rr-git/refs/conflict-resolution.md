# Merge conflict resolution

**When:** Conflict markers in the work tree (merge, rebase, cherry-pick). Use `git -C "$REPO_ROOT"` per [repo-root.md](repo-root.md).

## Workflow

1. List conflicting files with a **short** inventory — prefer `git diff --name-only --diff-filter=U` plus conflict markers. On large merges, add `git diff --cached --stat` (summary only). Do **not** dump full `git status` porcelain into context when hundreds of paths are staged.
2. For each conflict, assess per the table. High confidence → resolve immediately. Low → `git log -p` / `git blame` on the region; reassess. Still low → show the chunk to the user.
3. Minimal correctness-first edits; prefer keeping both sides when additive and non-overlapping.
4. Regenerate lockfiles with the package manager; do not hand-merge them when a tool exists.
5. **Resolve content** — `git add` only the files you resolved (plus regenerated lockfiles). Summarize choices. Do **not** agent-run full-tree compile/lint/test over auto-staged merge results; repo hooks own that on commit (or a user-approved scoped check).
6. **Finish commit** — Before `git commit` completing a merge/rebase:
   - Staged scale: `n=$(git diff --cached --name-only | wc -l | tr -d ' ')`; `git diff --cached --stat`.
   - Hooks likely when `.husky/pre-commit` or a `lint-staged` config exists at `$REPO_ROOT`.
   - If hooks likely **and** `n ≥ 50` → warn the user (duration / noise risk) before committing. Do **not** default to `--no-verify`.
   - Run the commit; await **quietly** (exit code / terminal footer only). **Stop:** never Read full hook/lint-staged progress streams into context.

## Confidence

| Conflict type | Confidence | Action |
| ------------- | ---------- | ------ |
| Additive, no overlap | High | Keep both |
| Formatting / import order only | High | Auto-resolve |
| One side reverts; other adds | High after log | Auto-resolve |
| Same region, both changed logic | Low | Investigate, else escalate |

## Guardrails

- Do not leave conflict markers.
- No broad refactors while resolving.
- Do not push or tag during conflict resolution.
- Never ingest full pre-commit/lint-staged output into the chat context.
