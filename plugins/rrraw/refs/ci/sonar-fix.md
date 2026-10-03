# Sonar fix (`--fix --sonar`)

Remediate open SonarQube issues for a PR or branch. Script lists; agent applies edits. **Not** a substitute for `code-quality-reports` (CI-published CQ JSON).

**PR-scoped success:** when the list envelope has `result.pull_request` (or the user passed `--pr`), done means the **PR tip is clean on CI** after remediations are committed and pushed — not a local edit summary alone. **Branch-only** (`--branch` / no open PR): local remediations + counts only (no commit/push/CI wait).

**Invoke list:** parent CLI contract — `sonar-list-issues --lean` via s-ci scripts / forge skill **Sonar fix** row (see parent `scripts/README.md` / `SCRIPTS-SPEC.md` for branch keys). Co-load [fix/pipeline-fix-rules.md](fix/pipeline-fix-rules.md) — honor its weaken ban; do not restate it here. **Wait primitives:** forge skill / `pre-merge-status` (GitHub `gh run watch RUN_ID --exit-status` in `skills/s-gh/refs/cli.md`) — do not invent sleep/backoff pollers.

## When

Task-shape is `--fix --sonar` (optional `--pr <id>` or `--branch <name>`). Do not use for general implement/refactor.

## Procedure

1. **Deps** — If `sonar-list-issues` returns `ok: false` with `sonar_not_found` / auth errors → stop; tell the user to install/authenticate `sonarqube-cli`. If `missing_project` → pass `-p` after discovering nested `sonar-project.properties` (CLI also searches depth≤3). If `ambiguous_project` → AskQuestion once with the listed keys (or user `-p`). Done: CLI available or stopped.
2. **List** — Run `s-ci sonar-list-issues --lean` **without** scope flags unless the user passed `--pr` / `--branch` (map to `--pull-request` / `--branch`). Default: CLI auto-resolves the **open PR/MR for the current branch** (`result.pull_request`). Parse `result.total` + `result.by_file`. Full `issues[]` only if the user asked list-only (no `--fix`) — omit `--lean` then. **Anti-trigger:** do **not** emit a human markdown issue table on this path — work from the envelope only. Done: envelope in context; record whether this run is **PR-scoped** (`result.pull_request` or user `--pr`).
3. **Empty / no PR** — If `no_open_pr` / `forge_unknown` → stop with that error (or user passes `--branch` / `--pr`). If `total == 0`: **corroborate before stop** (do not trust lean zero alone). On GitHub with a known PR number: fetch the SonarCloud / SonarQube Code Analysis check-run annotations for that PR (`gh api …/check-runs/…/annotations` or equivalent). If `annotations_count > 0` (or annotations non-empty), map path/line/title into a working `by_file` set and continue to Rules — **do not** report zero. Prefer this probe over Sonar MCP project search or dashboard WebFetch. If corroboration is also empty → for **branch-only**, report `Sonar: 0 open issues` and stop; for **PR-scoped**, skip Edit and continue at **Wait CI** (step 8) to confirm tip clean. Done.
4. **Rules (batch)** — Collect unique `rule` keys from `by_file` rows; look up each rule once (Sonar MCP `show_rule` or equivalent) **in one parallel turn**. Done: rule guidance cached per key.
5. **Edit (batch)** — For each path in `by_file`, apply minimal remediations that satisfy the rules (preserve behavior). No scanner weaken / blanket disables (pipeline-fix-rules). Done: edits applied or file skipped with reason.
6. **Summary** — Report counts only: `fixed` / `skipped` / `failed` (+ one line per failed key). Do not paste the full issue list unless the user explicitly asked list-only (no `--fix`). **Anti-trigger (PR-scoped):** do **not** treat Summary as terminal when remediations changed the tree or the tip is still CI/Sonar-dirty — continue Ship → Wait → re-enter.
7. **PR ship (PR-scoped only)** — Branch-only → skip to Stop (local done after Summary). If the working tree has Sonar remediation diffs: commit **only** those paths (short why-focused message; no secrets; honor repo hooks — no `--no-verify`); push to the existing PR tip branch. Do **not** open a second PR/MR; do **not** rewrite history. If `fixed == 0` and the tree is clean → skip commit/push and continue at Wait. Done: tip SHA on the remote PR head (or already clean tree). Stop: commit/push/auth/hook failure → escalate with evidence (do not claim CI clean).
8. **Wait CI (PR-scoped only)** — Resolve the tip’s pipeline run. Prefer allowlisted blocking wait (`gh run watch RUN_ID --exit-status` on GitHub; forge equivalent on GitLab). Else `pre-merge-status <PR#>` with ~30–60s backoff. Pending checks = wait, not FAIL. Wall timeout ~30 min → hard-stop with one-line reason. Done: checks left the pending set (success or failure).
9. **CI verdict / re-enter (PR-scoped only)** — Run `pre-merge-status <PR#>` (or equivalent). **Clean:** `verdict == ready` (or pipeline success with no blocking quality/Sonar blockers) **and** a fresh `sonar-list-issues --lean` shows `total == 0` after step-3 corroboration → **stop success** (report epochs used + final tip SHA). **Sonar/quality dirty:** re-enter from **List** (step 2) with the same PR scope — this is the in-session remediation interaction for new findings. Count each push→wait cycle as one **epoch**; `epoch_cap: 5`. **Non-Sonar job failure:** stop and point at `debug-pipeline` (do not expand into general implement). Hitting `epoch_cap` without clean → hard-stop.

## Stop

- Missing Sonar CLI/auth → escalate (`env`), no invented findings.
- No open PR/MR for current branch and no `--branch`/`--pr` → stop (`no_open_pr`).
- Branch-only: `total == 0` **and** forge check-run corroboration empty → `Sonar: 0 open issues`; after edits, Summary counts are enough (no CI loop).
- PR-scoped: stop **only** on clean CI + empty Sonar (step 9), hard-stop (`epoch_cap`, wait timeout, commit/push failure), or non-Sonar escalate — **never** after local Summary alone when remediations were applied or the tip is still dirty.
- Only weaken/bypass path → stop per pipeline-fix-rules.
