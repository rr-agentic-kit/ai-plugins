---
name: s-gh
disable-model-invocation: true
description: /s-gh — GitHub PR, issue, Actions; ship routes, --fix [<url|id>], --fix --sonar, --pull-dependabot; gh/MCP apply.
---

# s-gh

**Human overview:** [README.md](README.md)

**Shared policy:** `refs/ci/` — shapes, templates, fix/sonar rules.

**CLI:** `uv run --project skills/s-ci/scripts rr-ci <command>` — `skills/s-ci/scripts/README.md`, `skills/s-ci/SCRIPTS-SPEC.md`.

## Purpose

GitHub **apply layer**: PR/issue/Actions/review through **gh** (or MCP). Load `refs/ci/**` for policy; this skill owns task rows, [refs/cli.md](refs/cli.md), and scripts.

## When to use

- GitHub remote (direct `/s-gh` or delegated from **s-ci**)
- Open or update a PR (including commit/push): `--create-pr` / `--update-pr` / `--add-pr` / `-pr-mr` aliases — all upsert
- Optional `--draft` with ship — disk title/body gate per `refs/ci/task-shapes.md`
- Draft/create GitHub issue (including cross-repo `owner/repo`)
- Pipeline / Actions failure, CI reports, review submit
- **`--fix [<run|job URL|PR id>]`** — pipeline fix per `refs/ci/fix/pipeline-fix.md`
- **`--fix --sonar`** — per `refs/ci/sonar-fix.md`
- **`--pull-dependabot`** — per `refs/ci/pull-dependabot.md` (GitHub only)

## When not to use

- GitLab → **s-glab**
- Local git without PR → **s-git**
- Publish/deploy → **s-publish** / **s-deploy**
- Forge unknown → **s-ci** (detect + delegate)

## Procedure

TodoWrite: `refs/ci/task-shapes.md`. Skip **s-ci** forge step when entered direct and origin is GitHub.

1. **root** — `REPO_ROOT` via `skills/s-git/refs/repo-root.md`. Safety ref when history rewrite / discard possible.
2. **title** — **PR ship only.** Load `refs/ci/pr-mr-templates.md`. Skip for issue, `--fix`, `--fix --sonar`, `--pull-dependabot`.
3. **load** — Read [refs/cli.md](refs/cli.md); run `mr-add-preflight` when PR ship. Co-load `refs/ci/**` rows per task-shape.
4. **execute** — Matching task row below. Stop on first hard failure.

| Task | Read / run |
|------|------------|
| gh syntax | [refs/cli.md](refs/cli.md) |
| **Issue create** | Steps **Issue create** below |
| **PR ship** | `mr-add-preflight` then **Default PR ship** below |
| **Pipeline fix** (`--fix`) | `refs/ci/fix/pipeline-fix.md` + `debug-pipeline`; verify via `wait-run.py`, `pre-merge-status`, `gh run rerun` |
| Review comments on diff lines | `mr-ci-review-preflight` then [refs/inline-comments.md](refs/inline-comments.md) |
| **Open review threads** | `scripts/open-review-threads.sh` |
| **Reply to thread** | `scripts/open-review-threads.sh --reply <thread_id> --body "…"` |
| **Fix current-PR threads** | `refs/ci/review-comment-triage.md`; edit branch; reply with thread `id` |
| **Wait for Actions run** | `scripts/wait-run.py RUN_ID` `[--repo owner/repo]` |
| Failed Actions run | `debug-pipeline` `[PR_NUMBER\|RUN_URL]` |
| Code scanning / quality | `code-quality-reports` |
| **Sonar fix** (`--fix --sonar`) | `refs/ci/sonar-fix.md` + `sonar-list-issues --lean` |
| Security / Dependabot / code scanning | `pipeline-security-reports` |
| Resolve review threads | `mr-skip-threads` |
| PR add preflight | `mr-add-preflight` |
| Review body note | `mr-ensure-review-instructions` |
| Review decision | `mr-review-submit` |
| Pending reviews | `pending-reviews` |
| Workflow `if:` / artifact paths | [refs/workflow-rules.md](refs/workflow-rules.md) |
| MCP fallback | [refs/mcp.md](refs/mcp.md) |

**Fallback:** named `s-ci` subcommand from `skills/s-ci/SCRIPTS-SPEC.md` if listed; else stop.

### Issue create

1. Draft title + body in chat (or body file under `.ai/ci/` if large).
2. AskQuestion: **Create as drafted** | **Edit draft** | **Abort**. Stop on Abort.
3. On approve: `gh issue create --repo <forge-target> --title "…" --body "…"`. Syntax: [refs/cli.md](refs/cli.md).

### Default PR ship

One upsert path for all ship routes. Title/body from step **title** (prefer `.ai/ci/pr-mr-title.txt` + `.ai/ci/pr-mr-body.md` when present). After `mr-add-preflight`, branch on `result.status`:

- **`exists`** — push if needed; `gh pr edit` title/body/base when needed. Do **not** convert ready↔draft.
- **`ready_create`** — `gh pr create --draft --base <base_branch> …`. Always forge `--draft` + `--base` from preflight.
- Other preflight statuses → stop or escalate per envelope.

### Pre-merge

Run `pre-merge-status` once; branch on `result.verdict` / `result.blockers`. Do **not** invent poll chains — use `wait-run.py` when run id known.

## Invariants

- Policy in `refs/ci/**` — do not restate templates or fix rules here.
- After workflow fixes: commit/push allowed; re-run with `gh run rerun RUN_ID --failed`.
- Do not invent `gh` flags — [refs/cli.md](refs/cli.md) + task rows only.
- Inline comments: [refs/inline-comments.md](refs/inline-comments.md).
- Never open a second PR for the same branch.
