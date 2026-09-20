# Repository root (`REPO_ROOT`)

**When:** Before `git`, `gh`, or `glab` for ship or local git skills. The workspace folder may be a parent of the clone.

## What counts

`REPO_ROOT` is the work tree root — where the main `.git` lives. Not `src/` or a package subdirectory.

## Resolve (order)

1. **Explicit** — `--repo <path>` or `-C <path>` (workspace-relative or absolute). Validate via helper below.
2. **Shorthand** — first token is an existing directory → validate via helper.
3. **Default** — omit `--candidate` (cwd toplevel). If helper exits non-zero → **stop**. Do not walk parents to guess a repo.

## Helper

From `$REPO_ROOT` candidate or cwd, run (plugin-root relative):

```bash
python3 <rrraw-plugin>/skills/rr-git/scripts/resolve_repo_root.py
python3 <rrraw-plugin>/skills/rr-git/scripts/resolve_repo_root.py --candidate <path>
```

Parse stdout: `status`, `repo_root` (on ok). Exit `0` = set `REPO_ROOT` from `repo_root`. Exit `1` = abort (`error`/`message`/`remediation`). Details: [scripts/README.md](../scripts/README.md). Do **not** reinvent `rev-parse` / `pwd -P` invent chains.

## Execute

- `git -C "$REPO_ROOT" …`
- `gh` / `glab`: cwd = `REPO_ROOT`
- MCP: infer project from `git -C "$REPO_ROOT" remote get-url origin`
