# rr-ci CLI surface

Skill owns *when* to run; [scripts/README.md](scripts/README.md) owns *how*. This file owns command names, flags, and `result`/`error` keys. No Renovate commands.

## Envelope

`command`, `ok`, `result`, `error: {code, message}`. Exit `0` / `1` / `2`.

## Command whitelist

| Command | Agent branches / reports on |
|---------|-----------------------------|
| `detect-remote` | `result.forge` (`github` \| `gitlab` \| `unknown`); `result.host`; `result.owner`; `result.repo` |
| `debug-pipeline` | optional IID/PR number, `--save-log`; `result.status`; `result.error_lines`; `result.failed_job_id` |
| `code-quality-reports` | `result.reports.count` + `result.reports.nodes` |
| `pipeline-security-reports` | `result.status` ∈ `clean` \| `blocking_findings` \| `no_pipeline` \| `no_reports`; `result.findings.*`; `result.merge_blocked` |
| `mr-skip-threads` | `[IID]`, `--dry-run`; `unresolved_count` / `ok_count` / `fail_count` |
| `mr-add-preflight` | `--continue-anyway`, `--same-name-push`, `--branch-name`, `--commit-all`, `--commit-staged`; `result.status` ∈ `exists` \| `error` \| `no_commits` \| `escalate_merged` \| `escalate_upstream` \| `needs_branch_from_default` \| `ready_create`; plus `mr_url`, `message`, `upstream`, `staged_hint` |
| `mr-ensure-review-instructions` | `[IID]`, `--dry-run`; `ok`; optional `result.action` |
| `mr-ci-review-preflight` | optional `mr_ref`; `result.mr_iid`, branches, `merge_base`, `head_ref`, `read_ref`, `ref_range`, `allowlist`, `scope`, `diff_refs` |
| `mr-review-submit` | `--decision request-changes\|approve\|none`, `--dry-run`; `result.status` ∈ `requested_changes` \| `approved` \| `reviewer_only` \| `unchanged` \| `rejected` \| `would-submit`; `result.reviewer_added`, `result.mr_iid`; `result.reason` when `rejected` |
| `pending-reviews` | `result.count`, `result.urls` |

GitLab backend uses `glab`. GitHub backend uses `gh` with the **same** command names and result keys (PR number stands in for MR IID). `error.code` `forge_unknown` when detect-remote is `unknown` and `--forge` was not passed.

## Invoke

See [scripts/README.md](scripts/README.md).
