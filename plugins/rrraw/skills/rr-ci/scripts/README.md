# rr-ci CLI

JSON envelope on stdout. Stderr: progress. Parse JSON only.

## Invoke

From **target git repo** (cwd = repo root). Path is relative to the **rrraw plugin root**:

```bash
uv run --project skills/rr-ci/scripts rr-ci <command> [args]
```

Fallback: `python3 <plugin-root>/skills/rr-ci/scripts/cli.py <command> [args]` (Python ≥3.14).

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

## Commands

See [SCRIPTS-SPEC.md](../SCRIPTS-SPEC.md). Backends: GitLab (`glab`) and GitHub (`gh`). Forge-agnostic: `detect-remote`, `sonar-list-issues` (requires `sonar` on PATH; project key from `-p` or `sonar-project.properties`; default PR/MR = open for current branch via `gh`/`glab`).