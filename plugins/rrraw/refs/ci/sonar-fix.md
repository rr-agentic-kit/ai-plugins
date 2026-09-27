# Sonar fix (`--fix --sonar`)

Remediate open SonarQube issues for a PR or branch. Forge skill lists once; agent applies edits. **Not** a substitute for CI-published code-quality reports.

Co-load [fix/pipeline-fix-rules.md](fix/pipeline-fix-rules.md) — honor its weaken ban; do not restate it here.

## When

Task-shape is `--fix --sonar` (optional `--pr <id>` or `--branch <name>`). Do not use for general implement/refactor.

## Procedure

1. **Deps** — If the forge **Sonar fix** list row returns `ok: false` with missing CLI/auth → stop; tell the user to install/authenticate Sonar tooling. If `missing_project` → pass project key after discovering nested `sonar-project.properties`. If `ambiguous_project` → AskQuestion once with the listed keys (or user override). Done: CLI available or stopped.
2. **List (once)** — Run the active forge skill **Sonar fix** row **without** extra scope flags unless the user passed `--pr` / `--branch`. Default: open PR/MR for the current branch. Parse `result.total` + `result.by_file`. Full `issues[]` only if the user asked list-only (no `--fix`). **Anti-trigger:** do **not** emit a human markdown issue table on this path — work from the envelope only. Done: envelope in context.
3. **Empty / no PR** — If `no_open_pr` / `forge_unknown` → stop with that error (or user passes `--branch` / `--pr`). If `total == 0`: **corroborate before stop** (do not trust lean zero alone). On GitHub with a known PR number: use the forge skill check-run annotation probe for that PR. If annotations non-empty, map path/line/title into a working `by_file` set and continue to Rules — **do not** report zero. Prefer this probe over Sonar MCP project search or dashboard WebFetch. If corroboration is also empty → report `Sonar: 0 open issues` and stop. Done.
4. **Rules (batch)** — Collect unique `rule` keys from `by_file` rows; look up each rule once (Sonar MCP `show_rule` or equivalent) **in one parallel turn**. Done: rule guidance cached per key.
5. **Edit (batch)** — For each path in `by_file`, apply minimal remediations that satisfy the rules (preserve behavior). No scanner weaken / blanket disables (pipeline-fix-rules). Done: edits applied or file skipped with reason.
6. **Summary** — Report counts only: `fixed` / `skipped` / `failed` (+ one line per failed key). Optional: suggest re-analysis. Do not paste the full issue list unless the user explicitly asked list-only (no `--fix`).

## Stop

- Missing Sonar CLI/auth → escalate (`env`), no invented findings.
- No open PR/MR for current branch and no `--branch`/`--pr` → stop (`no_open_pr`).
- `total == 0` **and** forge check-run corroboration empty → stop (`Sonar: 0 open issues`).
- Only weaken/bypass path → stop per pipeline-fix-rules.
