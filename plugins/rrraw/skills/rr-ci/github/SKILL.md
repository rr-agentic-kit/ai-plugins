---
name: github
disable-model-invocation: true
user-invocable: false
description: GitHub-specific PR, issue, Actions, and gh/MCP patterns. Loaded by rr-ci after detect-remote returns github — not listed as a top-level plugin skill.
---

# rr-ci / GitHub

Loaded only from parent **rr-ci** `SKILL.md` when `result.forge` is `github`.

## Purpose

Route GitHub PR, **issue**, Actions, review, and check-run work through **gh** (if installed) or GitHub MCP. Generic PR/MR title/description rules stay in parent `refs/pr-mr-templates.md`.

## When to use

Parent **rr-ci** already selected GitHub. Do not load for GitLab remotes.

## When not to use

- GitLab MRs / `glab` → sibling **gitlab** skill
- Local git without a PR → **rr-git**
- Helm/K8s/Argo → sibling **deployment** skill
- Pages/releases/packages → sibling **publish** skill

## Procedure

1. **Tool** — `which gh`; if missing, [refs/mcp.md](refs/mcp.md). Done: gh or MCP.
2. **CLI** — `uv run --project <rrraw-plugin>/skills/rr-ci/scripts rr-ci <command>` (parent `scripts/README.md`). Same command names as GitLab; GitHub backend maps them. Done: envelope parsed. For issue create, use allowlisted `gh` in [refs/cli.md](refs/cli.md) — not an `rr-ci` subcommand.
3. **Forge target** — If parent set forge target `owner/repo`, pass `--repo owner/repo` on every `gh` issue/PR call that must hit that project. Default: cwd origin from `detect-remote`.
4. **Task row:**

| Task | Read / run |
|------|------------|
| gh syntax | [refs/cli.md](refs/cli.md) |
| **Issue create** | Steps **Issue create** below |
| **PR ship** | `mr-add-preflight` then **Default PR ship** below |
| Review comments on diff lines | `mr-ci-review-preflight` then [refs/inline-comments.md](refs/inline-comments.md) — GitHub `diff_refs` may be empty until parity; still run preflight for allowlist/MR metadata |
| Thread disposition / reply | Parent `refs/review-comment-triage.md` (Read from rr-ci root; do not invent path) |
| Failed Actions run | `debug-pipeline` `[PR_NUMBER]` — `result.status`, `result.error_lines`, `result.failed_job_id` (check-run / job id) |
| Code scanning / quality | `code-quality-reports` |
| **Sonar fix** (`--fix --sonar`) | Parent `refs/sonar-fix.md` + `sonar-list-issues --lean` (default: open PR for current branch) |
| Security / Dependabot / code scanning | `pipeline-security-reports` — treat `merge_blocked` as merge-state dirty when GitHub reports failing required checks |
| Resolve review threads | `mr-skip-threads` |
| PR add preflight | `mr-add-preflight` |
| Review body note | `mr-ensure-review-instructions` |
| Review decision | `mr-review-submit` (`gh pr review`) |
| Pending reviews | `pending-reviews` |
| Workflow `if:` / artifact paths | [refs/workflow-rules.md](refs/workflow-rules.md) |
| MCP fallback | [refs/mcp.md](refs/mcp.md) |

**Fallback (no matching row):** Use the named `rr-ci` subcommand from parent `SCRIPTS-SPEC.md` if listed; else stop — do not invent `gh` flags or issue workflows.

Done: matching row applied (ref loaded or CLI run). Stop: hard failure (`ok: false`, auth missing, preflight escalate).

### Issue create

1. Draft title + body in chat (or body file under `.ai/ci/` if large). Done: draft shown.
2. AskQuestion (or prose options): **Create as drafted** | **Edit draft** | **Abort**. Stop on Abort.
3. On approve: `gh issue create --repo <forge-target> --title "…" --body "…"` (omit `--repo` when target is cwd origin). Syntax: [refs/cli.md](refs/cli.md). Done: issue URL reported. Stop: create fails or auth missing.

### Default PR ship

For `--create-pr` / `--update-pr` / `--add-pr` / `--create-pr-mr` / `--update-pr-mr` / `--add-pr-mr` / prose “create|open|update|add PR” — **one upsert path**. Title/body: parent step **title** (after skill `--draft` gate if any, prefer `.ai/ci/pr-mr-title.txt` + `.ai/ci/pr-mr-body.md` when present). Pass handoff/user base as `mr-add-preflight --base <name>` when known. After `mr-add-preflight`, use `result.base_branch` on forge create/edit. Branch on `result.status`:

- **`exists`** — push commits if needed; `gh pr edit --title … --body-file …` when title/body should change; `gh pr edit --base <base_branch>` when the PR base differs from `result.base_branch`. Do **not** convert ready↔draft. Done: existing PR URL (`result.mr_url`). Never open a second PR for the branch.
- **`ready_create`** — `gh pr create --draft --base <base_branch> --fill --title "…" --body-file …`. Always pass forge `--draft` and `--base` from preflight. Do **not** invent merge-method flags on create. Done: draft PR created. Stop: create fails.
- Other preflight statuses (`error`, `no_commits`, `escalate_*`, `needs_branch_from_default`) → stop or escalate per envelope; do not invent a create.

Skill `--draft` is the parent human title/body gate — distinct from forge `--draft` (always on create).

### Pre-merge

When asked — run `pre-merge-status` once; branch on `result.verdict` / `result.blockers`; report one-line verdict. Do **not** invent five sequential probes. Done: report emitted. Stop: `verdict == blocked` (next action from `blockers`; `debug-pipeline` only when checks fail).

## Invariants

- After workflow fixes: commit/push allowed (parent rr-ci); re-run with `gh run rerun RUN_ID --failed`.
- Do not invent `rr-ci` subcommands — parent `SCRIPTS-SPEC.md`.
- Do not invent `gh` flags — only [refs/cli.md](refs/cli.md) + task rows above.
- Inline comment line/diff rules: [refs/inline-comments.md](refs/inline-comments.md).
- Create/update ship routes are aliases; never invent a second PR for the same branch.
