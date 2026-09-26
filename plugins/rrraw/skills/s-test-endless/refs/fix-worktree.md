# Fix worktree (test-endless workers)

**Audience:** `test-endless-fix` on isolated plan packs.

**Read order:** (1) this file — scope rules; (2) **`skills/s-git/refs/worktree-lifecycle.md`** — all git commands.

## When this applies

- **Delegated `Task`** implementing a plan pack **in isolation** → follow git ref with `<base>`, `<N>`, `<worktree_path>` / `<branch_name>` from parent.
- **Orchestrator** never edits application or test code directly.

## Definition of done (from worktree cwd)

Before merge-back: run **build**, **test** / **test:coverage**, and stack lint/checks via **Shell** with **`cwd`** = **`<worktree_path>`**. Resolve scripts from **`project-detection.md`**.

Formal **`test-endless-toolchain`** verify from **repository root** runs **after** all worker **`Task`**s for the iteration — worker Bash is in-worktree DoD only.

## Parallelism

Default **sequential** merges to `<base>`; orchestrator caps concurrent disjoint packs via **`--max-parallel`**.

## Base policy

**`<base>`** must be the integration branch from pre-flight — **never** `main` or `master`. Worker refuses protected trunk as merge target.
