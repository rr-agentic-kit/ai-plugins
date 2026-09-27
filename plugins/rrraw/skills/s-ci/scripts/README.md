# rr-ci CLI

JSON envelope on stdout. Stderr: progress. Parse JSON only.

## Invoke

From **target git repo** (cwd = repo root). Path is relative to the **rrraw plugin root**:

```bash
uv run --project skills/s-ci/scripts rr-ci <command> [args]
```

Fallback: `python3 <plugin-root>/skills/s-ci/scripts/cli.py <command> [args]` (Python ≥3.14).

Optional `--forge github|gitlab` overrides `detect-remote`.

## Envelope

```json
{
  "command": "detect-remote",
  "ok": true,
  "result": { "forge": "github", "host": "github.com", "owner": "acme", "repo": "app" },
  "error": null
}
```

**Exit codes:** `0` = `ok` true; `1` = hard failure; `2` = usage.

## Disk sidecars

All files written by this CLI land under **`.ai/ci/`** (repo root), never the worktree root.

| Flag / command | Path | Envelope |
|----------------|------|----------|
| `debug-pipeline --save-log` | `.ai/ci/job-<id>.log` | `result.log_path` (repo-relative) |
| `debug-pipeline --artifacts` | `.ai/ci/artifacts/<id>/` | `result.artifacts_dir` (repo-relative) |

```bash
# Branch fallback (current branch latest run / MR pipeline)
uv run --project skills/s-ci/scripts rr-ci debug-pipeline --save-log

# Explicit GitHub run URL (cross-repo via URL owner/repo)
uv run --project skills/s-ci/scripts rr-ci debug-pipeline \
  'https://github.com/acme/app/actions/runs/123456789' --save-log --artifacts

# Explicit GitLab job URL
uv run --project skills/s-ci/scripts rr-ci debug-pipeline \
  'https://gitlab.com/acme/app/-/jobs/987654' --save-log

# Explicit ids
uv run --project skills/s-ci/scripts rr-ci debug-pipeline --run-id 123 --job-id 456
```

## Commands

See [SCRIPTS-SPEC.md](../SCRIPTS-SPEC.md). Backends: GitLab (`glab`) and GitHub (`gh`). Forge-agnostic: `detect-remote`, `sonar-list-issues` (requires `sonar` on PATH; project key from `-p` or `sonar-project.properties`; default PR/MR = open for current branch via `gh`/`glab`; `--lean` for `--fix --sonar`). New helpers: `mr-inline-anchors` (`+` new_line set), `pre-merge-status` (one verdict envelope).