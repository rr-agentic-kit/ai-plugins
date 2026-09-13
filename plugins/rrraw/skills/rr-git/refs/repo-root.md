# Repository root (`REPO_ROOT`)

**When:** Before `git`, `gh`, or `glab` for ship or local git skills. The workspace folder may be a parent of the clone.

## What counts

`REPO_ROOT` is the work tree root — where the main `.git` lives. Not `src/` or a package subdirectory.

## Resolve (order)

1. **Explicit** — `--repo <path>` or `-C <path>` (workspace-relative or absolute). Validate as below.
2. **Shorthand** — first token is an existing directory → validate.
3. **Default** — `git rev-parse --show-toplevel` in the current cwd. If it fails → **stop**. Do not walk parents to guess a repo.

## Validate user-supplied `candidate`

1. `TOP="$(git -C "$candidate" rev-parse --show-toplevel 2>/dev/null)"` — empty → abort.
2. `ABS="$(cd "$candidate" && pwd -P)"` — `cd` fails → abort.
3. If `ABS` ≠ `TOP` → abort: pass the repository root, not a subdirectory. Mention `TOP`.
4. Set `REPO_ROOT="$TOP"`.

## Execute

- `git -C "$REPO_ROOT" …`
- `gh` / `glab`: cwd = `REPO_ROOT`
- MCP: infer project from `git -C "$REPO_ROOT" remote get-url origin`
