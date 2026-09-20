# Sonar fix (`--fix --sonar`)

Remediate open SonarQube issues for a PR or branch. Script lists; agent applies edits. **Not** a substitute for `code-quality-reports` (CI-published CQ JSON).

**Invoke list:** parent `scripts/README.md` → `sonar-list-issues`. **Branch keys:** parent `SCRIPTS-SPEC.md`. Parent co-loads [pipeline-fix-rules.md](pipeline-fix-rules.md) — honor its weaken ban; do not restate it here.

## When

Parent task-shape is `--fix --sonar` (optional `--pr <id>` or `--branch <name>`). Do not use for general implement/refactor.

## Procedure

1. **Deps** — If `sonar-list-issues` returns `ok: false` with `sonar_not_found` / auth errors → stop; tell the user to install/authenticate `sonarqube-cli`. Done: CLI available or stopped.
2. **List (once)** — Run `rr-ci sonar-list-issues` **without** scope flags unless the user passed `--pr` / `--branch` (map to `--pull-request` / `--branch`). Default: CLI auto-resolves the **open PR/MR for the current branch** (`result.pull_request`). Parse `result.total` + `result.issues[]`. **Anti-trigger:** do **not** emit a human markdown issue table on this path — work from the envelope only. Done: envelope in context.
3. **Empty / no PR** — If `total == 0` → report `Sonar: 0 open issues` and stop. If `no_open_pr` / `forge_unknown` → stop with that error (or user passes `--branch` / `--pr`). Done.
4. **Rules (batch)** — Collect unique `rule` keys; look up each rule once (Sonar MCP `show_rule` or equivalent) **in one parallel turn**. Done: rule guidance cached per key.
5. **Edit (batch)** — Group issues by `file`; for each file, apply minimal remediations that satisfy the rules (preserve behavior). No scanner weaken / blanket disables (pipeline-fix-rules). Done: edits applied or file skipped with reason.
6. **Summary** — Report counts only: `fixed` / `skipped` / `failed` (+ one line per failed key). Optional: suggest re-analysis. Do not paste the full issue list unless the user explicitly asked list-only (no `--fix`).

## Stop

- Missing Sonar CLI/auth → escalate (`env`), no invented findings.
- No open PR/MR for current branch and no `--branch`/`--pr` → stop (`no_open_pr`).
- Only weaken/bypass path → stop per pipeline-fix-rules.
