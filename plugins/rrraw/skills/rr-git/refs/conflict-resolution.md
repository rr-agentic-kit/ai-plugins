# Merge conflict resolution

**When:** Conflict markers in the work tree (merge, rebase, cherry-pick). Use `git -C "$REPO_ROOT"` per [repo-root.md](repo-root.md).

## Workflow

1. List conflicting files from `git status` and conflict markers.
2. For each conflict, assess per the table. High confidence → resolve immediately. Low → `git log -p` / `git blame` on the region; reassess. Still low → show the chunk to the user.
3. Minimal correctness-first edits; prefer keeping both sides when additive and non-overlapping.
4. Regenerate lockfiles with the package manager; do not hand-merge them when a tool exists.
5. Run compile/lint/relevant tests from `$REPO_ROOT`. Stage with `git add`. Summarize choices.

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
