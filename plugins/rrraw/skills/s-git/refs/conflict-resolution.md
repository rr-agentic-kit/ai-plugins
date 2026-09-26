# Merge conflict resolution

**When:** Conflict markers in the work tree (merge, rebase, cherry-pick). Use `git -C "$REPO_ROOT"` per [repo-root.md](repo-root.md).

## Workflow

1. List conflicting files with a **short** inventory — prefer `git diff --name-only --diff-filter=U` plus conflict markers. On large merges, add `git diff --cached --stat` (summary only). Do **not** dump full `git status` porcelain into context when hundreds of paths are staged.
2. **Version fields first** — From `$REPO_ROOT`, run `resolve_version_conflicts.py` (`--plan` then `--apply`). Invoke + stdout/exit contract: [scripts/README.md](../scripts/README.md). Required parse keys: `status`, `resolved`, `files_remaining`. Exit `2` = versions fixed, other conflicts remain → continue below. Policy: **latest semver wins** on known version loci — field-scoped only; see Guardrails. Do **not** Read whole manifests to pick ours/theirs for version.
3. For each **remaining** conflict, assess per the table. High confidence → resolve immediately. Low → `git log -p` / `git blame` on the region; reassess. Still low → show the chunk to the user.
4. Minimal correctness-first edits; prefer keeping both sides when additive and non-overlapping.
5. Regenerate lockfiles with the package manager; do not hand-merge them when a tool exists.
6. **Resolve content** — `git add` only the files you resolved (plus regenerated lockfiles). Summarize choices. Do **not** agent-run full-tree compile/lint/test over auto-staged merge results; repo hooks own that on commit (or a user-approved scoped check).
7. **Finish commit** — Before `git commit` completing a merge/rebase, run `finish_commit_preflight.py` (see [scripts/README.md](../scripts/README.md)). Parse `staged_count`, `hooks_likely`, `warn`. If `warn=yes` → warn the user (duration / noise risk) before committing. Do **not** default to `--no-verify`. Optionally `git diff --cached --stat` for a short summary. Run the commit; await **quietly** (exit code / terminal footer only). **Stop:** never Read full hook/lint-staged progress streams into context.

## Confidence

| Conflict type | Confidence | Action |
| ------------- | ---------- | ------ |
| Version field (semver / `version` key) | High | Run `resolve_version_conflicts.py` — **latest wins**; do not ask |
| Additive, no overlap | High | Keep both |
| Formatting / import order only | High | Auto-resolve |
| One side reverts; other adds | High after log | Auto-resolve |
| Same region, both changed logic | Low | Investigate, else escalate |

## Guardrails

- Do not leave conflict markers (except while mid-resolution before the finish commit).
- **Never** whole-file `ours`/`theirs` checkout to resolve version loci — field-scoped latest only; co-hunk prose stays conflicted until judged.
- **Never** ask the user to pick a version when both sides parse as versions — latest semver is mandatory.
- **Never** prefer branch identity (ours/theirs) over semver for version fields.
- No broad refactors while resolving.
- Do not push or tag during conflict resolution.
- Never ingest full pre-commit/lint-staged output into the chat context.
