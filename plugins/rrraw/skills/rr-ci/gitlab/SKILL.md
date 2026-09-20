---
name: gitlab
disable-model-invocation: true
description: GitLab MR, issue, pipeline, glab/MCP, and .gitlab-ci.yml. Loaded by rr-ci when detect-remote returns gitlab — not a top-level plugin skill.
---

# rr-ci / GitLab

Loaded only from parent **rr-ci** `SKILL.md` when `result.forge` is `gitlab`.

## Purpose

Route GitLab MR, **issue**, pipeline, discussion, and CI report work through **glab** (if installed) or **GitLab MCP**. Generic PR/MR title/description rules stay in parent `refs/pr-mr-templates.md`.

## When to use

Parent **rr-ci** already selected GitLab. Do not load for GitHub remotes.

## When not to use

- GitHub PRs / Actions → sibling **github** skill
- Local git without an MR → **rr-git**
- Helm/K8s/Argo deploy mechanics → sibling **deployment** skill
- Pages/registry publish → sibling **publish** skill

## Procedure

1. **Tool** — `which glab`; if missing, [refs/mcp.md](refs/mcp.md). Done: glab or MCP.
2. **CLI** — From target repo: `uv run --project <rrraw-plugin>/skills/rr-ci/scripts rr-ci <command>` (parent `scripts/README.md`). Done: envelope parsed. For issue create, use allowlisted `glab` in [refs/cli.md](refs/cli.md) — not an `rr-ci` subcommand.
3. **Forge target** — If parent set forge target `owner/repo` (or GitLab path), pass `--repo` on issue/MR calls that must hit that project. Default: cwd origin from `detect-remote`.
4. **Task row** — Read only the matching ref:

| Task | Read / run |
|------|------------|
| glab syntax | [refs/cli.md](refs/cli.md) |
| **Issue create** | Steps **Issue create** below |
| **MR ship** | `mr-add-preflight` then **Default MR ship** below |
| Inline MR threads | `mr-ci-review-preflight` then optional `mr-inline-anchors`, then [refs/inline-comments.md](refs/inline-comments.md) |
| Thread disposition / reply | Parent `refs/review-comment-triage.md` (Read from rr-ci root; do not invent path) |
| Resolve open MR | [refs/mr-resolve.md](refs/mr-resolve.md) |
| Failed pipeline | `debug-pipeline` `[MR_IID]` — branch on `result.status`, `result.error_lines`, `result.failed_job_id` |
| CI code-quality | `code-quality-reports` — `result.reports.count`, `result.reports.nodes` |
| **Sonar fix** (`--fix --sonar`) | Parent `refs/sonar-fix.md` + `sonar-list-issues --lean` (default: open MR for current branch) |
| Pipeline security | `pipeline-security-reports` — `result.merge_blocked`, `result.findings.*` |
| Bulk resolve threads | `mr-skip-threads` |
| MR add preflight | `mr-add-preflight` |
| Review instructions note | `mr-ensure-review-instructions` |
| Review decision | `mr-review-submit` |
| Pending reviews | `pending-reviews` |
| `rules:` / artifact paths | [refs/pipeline-rules.md](refs/pipeline-rules.md) |
| Code-quality when-to-use | [refs/code-quality-reports.md](refs/code-quality-reports.md) |
| Security reports when-to-use | [refs/pipeline-security-reports.md](refs/pipeline-security-reports.md) |
| MCP fallback | [refs/mcp.md](refs/mcp.md) |

**Fallback (no matching row):** Use the named `rr-ci` subcommand from parent `SCRIPTS-SPEC.md` if listed; else stop — do not invent `glab` flags or issue workflows.

Done: matching row applied (ref loaded or CLI run). Stop: hard failure (`ok: false`, auth missing, preflight escalate).

### Issue create

1. Draft title + body in chat (or body file under `.ai/ci/` if large). Done: draft shown.
2. AskQuestion (or prose options): **Create as drafted** | **Edit draft** | **Abort**. Stop on Abort.
3. On approve: `glab issue create --repo <forge-target> -t "…" -d "…"` (omit `--repo` when target is cwd origin). Syntax: [refs/cli.md](refs/cli.md). Done: issue URL reported. Stop: create fails or auth missing.

### Default MR ship

For `--create-mr` / `--update-mr` / `--create-pr-mr` / `--update-pr-mr` / prose “create|open|update MR” — **one upsert path**. Title/body: parent step **title** (after `--draft` gate if any, prefer `.ai/ci/pr-mr-title.txt` + `.ai/ci/pr-mr-body.md` when present). After `mr-add-preflight`, branch on `result.status`:

- **`exists`** — push commits if needed; `glab mr update` with title/description from disk when they should change. Done: existing MR URL (`result.mr_url`). Never open a second MR for the branch.
- **`ready_create`** — `glab mr create --fill --yes --squash-before-merge --remove-source-branch` plus title/description (**no** forge `--draft` unless user asked for forge-draft status). Done: MR created. Stop: create fails.
- Other preflight statuses (`error`, `no_commits`, `escalate_*`, `needs_branch_from_default`) → stop or escalate per envelope; do not invent a create.

Skill `--draft` is the parent human gate — not this row’s forge `--draft` flag.

### Pre-merge

When asked — run `pre-merge-status` once; branch on `result.verdict` / `result.blockers`; report one-line verdict. Do **not** invent five sequential probes. Done: report emitted. Stop: `verdict == blocked` (next action from `blockers`; `debug-pipeline` only when pipeline fails).

## Invariants

- After pipeline fixes: commit/push allowed (parent rr-ci); retry with `glab ci retry JOB_ID`.
- Do not invent `rr-ci` subcommands — parent `SCRIPTS-SPEC.md`.
- Do not invent `glab` flags — only [refs/cli.md](refs/cli.md) + task rows above.
- Inline comment / `new_line` rules: [refs/inline-comments.md](refs/inline-comments.md).
- Create/update ship routes are aliases; never invent a second MR for the same branch.
