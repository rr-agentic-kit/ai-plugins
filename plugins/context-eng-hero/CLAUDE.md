# context-eng-hero — agent contract

This directory is the **entire installed plugin**. Marketplace installs ship only `plugins/context-eng-hero/` — not monorepo siblings.

## What does not exist here

When executing plugin commands or skills, treat these as **unavailable**:

- `tests/`, repo-root `pyproject.toml`, `uv.lock`, `../../`, `.github/`
- `CONTRIBUTING.md` at repo root (maintainers only; not in the install artifact)
- `pytest` or any contributor test harness

Do not reference paths outside this plugin tree unless the user explicitly provides another checkout.

## Python runtime

- **Version:** CPython **3.14+** for `scripts/audit_static.py` (modern syntax in script code).
- **Dependencies:** [`scripts/requirements.txt`](scripts/requirements.txt) (`pyyaml>=6.0,<7`).
- **Bootstrap:** Before the first static audit, if `import yaml` fails, from **plugin root**:

  ```bash
  python3 -m pip install -r scripts/requirements.txt
  ```

  Optional: `uv pip install -r scripts/requirements.txt` if `uv` is on PATH.  
  Optional venv: `python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt` then use `.venv/bin/python`.

- **Static audit:** cwd = plugin root; plugin-relative paths only:

  ```bash
  python3 scripts/audit_static.py . <relative-path>
  ```

- If install or run still fails: report **STATIC SKIPPED** with reason — do not silently omit static checks.

## No pytest in this tree

Regression tests live in the **ai-plugins monorepo** only. Do not run or expect `pytest` inside the installed plugin.

## Product behavior

Skill authors and action procedures: [`skills/context-engineer/SKILL.md`](skills/context-engineer/SKILL.md) and `skills/context-engineer/refs/`.
