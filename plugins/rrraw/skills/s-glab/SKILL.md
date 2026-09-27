---
name: s-glab
disable-model-invocation: true
description: /s-glab — GitLab MR, issue, pipeline; ship routes (--create-mr / …), --fix [<url|id>], --fix --sonar; glab/MCP apply.
---

# s-glab

**Human overview:** [README.md](README.md)

**Shared policy:** `refs/ci/` — shapes, templates, fix/sonar rules.

**CLI:** `uv run --project skills/s-ci/scripts rr-ci <command>` — `skills/s-ci/scripts/README.md`, `skills/s-ci/SCRIPTS-SPEC.md`.

## Purpose

GitLab **apply layer**: MR/issue/pipeline/review through **glab** (or MCP). Load `refs/ci/**` for policy; this skill owns task rows, [refs/cli.md](refs/cli.md), and forge refs.

## When to use

- GitLab remote (direct `/s-glab` or delegated from **s-ci**)
- Open or update an MR (including commit/push): `--create-mr` / `--update-mr` / `--add-mr` / `-pr-mr` aliases — all upsert
- Optional `--draft` with ship — disk title/body gate per `refs/ci/task-shapes.md`
- Draft/create GitLab issue (including cross-repo path)
- Pipeline failure, CI reports, review submit
- **`--fix [<job URL|MR iid>]`** — pipeline fix per `refs/ci/fix/pipeline-fix.md`
- **`--fix --sonar`** — per `refs/ci/sonar-fix.md`

## When not to use

- GitHub → **s-gh**
- Local git without MR → **s-git**
- Publish/deploy → **s-publish** / **s-deploy**
- **`--pull-dependabot`** — GitHub only (**s-gh**)
- Forge unknown → **s-ci**

## Procedure

TodoWrite: `refs/ci/task-shapes.md`. Skip **s-ci** forge step when entered direct and origin is GitLab.

1. **root** — `REPO_ROOT` via `skills/s-git/refs/repo-root.md`. Safety ref when history rewrite / discard possible.
2. **title** — **MR ship only.** Load `refs/ci/pr-mr-templates.md`. Skip for issue, `--fix`, `--fix --sonar`.
3. **load** — Read [refs/cli.md](refs/cli.md); run `mr-add-preflight` when MR ship. Co-load `refs/ci/**` rows per task-shape.
4. **execute** — Matching task row below. Stop on first hard failure.

| Task | Read / run |
|------|------------|
| glab syntax | [refs/cli.md](refs/cli.md) |
| **Issue create** | Steps **Issue create** below |
| **MR ship** | `mr-add-preflight` then **Default MR ship** below |
| **Pipeline fix** (`--fix`) | `refs/ci/fix/pipeline-fix.md` + `debug-pipeline`; verify via `pre-merge-status`, `glab ci retry` |
| Inline MR threads | `mr-ci-review-preflight` then optional `mr-inline-anchors`, then [refs/inline-comments.md](refs/inline-comments.md) |
| Thread disposition / reply | `refs/ci/review-comment-triage.md` |
| Resolve open MR | [refs/mr-resolve.md](refs/mr-resolve.md) |
| Failed pipeline | `debug-pipeline` `[MR_IID\|PIPELINE_OR_JOB_URL]` |
| CI code-quality | `code-quality-reports` |
| **Sonar fix** (`--fix --sonar`) | `refs/ci/sonar-fix.md` + `sonar-list-issues --lean` |
| Pipeline security | `pipeline-security-reports` |
| Bulk resolve threads | `mr-skip-threads` |
| MR add preflight | `mr-add-preflight` |
| Review instructions note | `mr-ensure-review-instructions` |
| Review decision | `mr-review-submit` |
| Pending reviews | `pending-reviews` |
| `rules:` / artifact paths | [refs/pipeline-rules.md](refs/pipeline-rules.md) |
| Code-quality when-to-use | [refs/code-quality-reports.md](refs/code-quality-reports.md) |
| Security reports when-to-use | [refs/pipeline-security-reports.md](refs/pipeline-security-reports.md) |
| MCP fallback | [refs/mcp.md](refs/mcp.md) |

**Fallback:** named `s-ci` subcommand from `skills/s-ci/SCRIPTS-SPEC.md` if listed; else stop.

### Issue create

1. Draft title + body in chat (or body file under `.ai/ci/` if large).
2. AskQuestion: **Create as drafted** | **Edit draft** | **Abort**. Stop on Abort.
3. On approve: `glab issue create --repo <forge-target> -t "…" -d "…"`. Syntax: [refs/cli.md](refs/cli.md).

### Default MR ship

One upsert path for all ship routes. Title/body from step **title** (prefer `.ai/ci/pr-mr-title.txt` + `.ai/ci/pr-mr-body.md` when present). After `mr-add-preflight`, branch on `result.status`:

- **`exists`** — push if needed; `glab mr update` title/description/target when needed. Do **not** convert ready↔draft.
- **`ready_create`** — `glab mr create --draft --target-branch <base_branch> …`. Always forge `--draft` + `--target-branch` from preflight.
- Other preflight statuses → stop or escalate per envelope.

### Pre-merge

Run `pre-merge-status` once; branch on `result.verdict` / `result.blockers`.

## Invariants

- Policy in `refs/ci/**` — do not restate templates or fix rules here.
- After pipeline fixes: commit/push allowed; retry with `glab ci retry JOB_ID`.
- Do not invent `glab` flags — [refs/cli.md](refs/cli.md) + task rows only.
- Inline / `new_line` rules: [refs/inline-comments.md](refs/inline-comments.md).
- Never open a second MR for the same branch.
