# rr-ci CLI surface

Skill owns *when* to run; [scripts/README.md](scripts/README.md) owns *how*. This file owns command names, flags, and `result`/`error` keys. No Renovate commands.

## Envelope

`command`, `ok`, `result`, `error: {code, message}`. Exit `0` / `1` / `2`.

## Command whitelist

| Command | Agent branches / reports on |
|---------|-----------------------------|
| `detect-remote` | `result.forge` (`github` \| `gitlab` \| `unknown`); `result.host`; `result.owner`; `result.repo` |
| `debug-pipeline` | optional IID/PR number, `--save-log` → `.ai/ci/job-<id>.log` + `result.log_path`; `result.status`; `result.error_lines`; `result.failed_job_id` |
| `code-quality-reports` | `result.reports.count` + `result.reports.nodes` |
| `sonar-list-issues` | forge-agnostic; default scope = open PR/MR for current branch; `result.project`, `result.total`, `result.issues[]` (`key`, `rule`, `severity`, `type`, `file`, `line`, `message`, `status`); `--lean` → `result.by_file` map path → `{key,rule,severity,line}[]` (omit full `issues[]`/messages); optional `pull_request` / `branch`; flags `-p/--project`, `--pull-request`, `--branch`, `--statuses`, `--lean`; project key from `-p` or `sonar-project.properties` at repo root **or** unique nested match depth≤3; when `sonar list` returns empty for a PR/branch, falls back once via `sonar api get` Issues Search; errors `no_open_pr`, `forge_unknown`, `sonar_not_found`, `missing_project`, `ambiguous_project` |
| `pipeline-security-reports` | `result.status` ∈ `clean` \| `blocking_findings` \| `no_pipeline` \| `no_reports`; `result.findings.*`; `result.merge_blocked` |
| `mr-skip-threads` | `[IID]`, `--dry-run`; `unresolved_count` / `ok_count` / `fail_count` |
| `mr-add-preflight` | `--continue-anyway`, `--same-name-push`, `--branch-name`, `--commit-all`, `--commit-staged`; `result.status` ∈ `exists` \| `error` \| `no_commits` \| `escalate_merged` \| `escalate_upstream` \| `needs_branch_from_default` \| `ready_create`; plus `mr_url`, `message`, `upstream`, `staged_hint` |
| `mr-ensure-review-instructions` | `[IID]`, `--dry-run`; `ok`; optional `result.action` |
| `mr-ci-review-preflight` | optional `mr_ref`; `result.mr_iid`, branches, `merge_base`, `head_ref`, `read_ref`, `ref_range`, `allowlist`, `scope`, `diff_refs` |
| `mr-inline-anchors` | optional `mr_ref`, repeatable `--path`; `result.mr_iid`, `result.diff_refs` (`base_sha`/`start_sha`/`head_sha`), `result.files` path → sorted `+` line ints; GitHub may set `result.note` on parity gap |
| `mr-review-submit` | `--decision request-changes\|approve\|none`, `--dry-run`; `result.status` ∈ `requested_changes` \| `approved` \| `reviewer_only` \| `unchanged` \| `rejected` \| `would-submit`; `result.reviewer_added`, `result.mr_iid`; `result.reason` when `rejected` |
| `pending-reviews` | `result.count`, `result.urls` |
| `pre-merge-status` | optional `mr_ref`; `result.verdict` ∈ `ready` \| `blocked`; `result.blockers[]`; compact `pipeline`/`checks`, `security.merge_blocked`, `unresolved_threads`, `reviews` |

GitLab backend uses `glab`. GitHub backend uses `gh` with the **same** command names and result keys (PR number stands in for MR IID). `error.code` `forge_unknown` when detect-remote is `unknown` and `--forge` was not passed.

## Invoke

See [scripts/README.md](scripts/README.md).
