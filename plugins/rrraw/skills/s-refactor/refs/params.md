# Refactor parameters (canonical)

**Purpose:** Define deterministic `rr-builder --refactor` argument parsing and the validated param block passed to the orchestrator.

**Audience:** **s-refactor** via **rr-builder** handoff or orchestrate refactor stage. Parse flags into this block **before** `Read`ing the refactor orchestrator skill. Unknown flags → **stop** with one-line error.

Paths in this doc are relative to **`PLUGIN_ROOT`** unless noted.

## Grammar

```text
[--scope MR|PR|all|full] [--epoch-cap N] [paths…]
```

Tokens are case-sensitive. Positional `paths…` narrow scope after flag parsing (directories, files, globs as today).

Accept one effective scope selector. Repeated equivalent selectors normalize to one; conflicting selectors stop: `conflicting scope selectors`.

## Scope

| Flag / token | Param | Meaning |
|--------------|-------|---------|
| (none) | `scope: MR` | Current branch vs integration base (merge-base → `HEAD`) |
| `--scope MR` | `scope: MR` | Same as default |
| `--scope PR` | `scope: MR` | Alias of `MR` (GitHub-shaped UX; same diff recipe) |
| `--scope all` | `scope: all` | Entire codebase (production source only) |
| `--scope full` | `scope: all` | Alias of `all` |

**Default:** `scope: MR` when omitted.

**Paths:** Positional `paths…` always narrow after scope resolution. With no `--scope`, default `scope: MR` then apply narrowers (e.g. `rr-builder --refactor src/foo/` → MR diff restricted to `src/foo/`).

**MR recipe:** `git merge-base HEAD '@{upstream}'`; on failure `origin/main` or `origin/master`; `git diff --name-only "$MERGE_BASE"..HEAD`. Positional paths narrow further. Same recipe as **s-review** report/fix scope.

**Production source filter:** Exclude test roots, generated output, vendored/third-party trees, and build artifacts from the resolved file list unless a positional path explicitly targets them.

**INVALID:** Path that does not exist → stop; one-line error.

**INVALID:** Unknown flag, missing flag value, or conflicting scope selectors → stop with the corresponding one-line error; do not guess precedence. `--scope=<value>` is unknown syntax; the grammar requires separate tokens.

Empty branch diff → clarify once (path or `all`). Empty resolved path/all scope → stop: `No files to refactor`.

## Epoch cap

| Flag | Param | Meaning |
|------|-------|---------|
| `--epoch-cap N` | `epoch_cap: N` | Max full-scope assessment epochs (default **5**) |

**INVALID:** `N < 1` or non-integer → stop: `invalid --epoch-cap`.

## Worktree

Inline fixes use the **main working tree** only — no isolated worktree.

## Param block (YAML)

```yaml
scope: MR | all
paths: []          # optional narrowers after scope resolution
epoch_cap: 5
```
