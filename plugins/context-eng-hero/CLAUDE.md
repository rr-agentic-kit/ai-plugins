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
- **Dependencies:** [`scripts/requirements.txt`](scripts/requirements.txt) (`pyyaml>=6.0,<7`, `jinja2>=3.1,<4`, `jsonschema>=4.23,<5`).
- **Bootstrap:** Before the first static audit or report render, if `import yaml` / `jinja2` / `jsonschema` fails, from **plugin root**:

  ```bash
  python3 -m pip install -r scripts/requirements.txt
  ```

  Optional: `uv pip install -r scripts/requirements.txt` if `uv` is on PATH.  
  Optional venv: `python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt` then use `.venv/bin/python`.

- **Static audit:** cwd = plugin root; plugin-relative paths only:

  ```bash
  python3 scripts/audit_static.py . <relative-path>
  ```

  Target outside this plugin tree (e.g. monorepo): pass a `plugin_root` that **contains** the target and a path relative to it — `python3 scripts/audit_static.py <repo-root> plugins/<other-plugin>/skills/<name>/SKILL.md` (run from repo root, or `plugins/context-eng-hero/scripts/audit_static.py` with repo-root as first arg). Parent-relative `../…` paths are rejected.

- **Improve report render:** `python3 scripts/render_ce_report.py <kind> --in <json> --out <md>` (kinds: `compliance`, `opportunity`, `apply-plan`, `reflection`). Exit **2** = schema/JSON error — fix lean JSON and re-run. The script only accepts paths **under this plugin root**; when improve scratch lives in the user project, render via the sanctioned sandbox fallback in [`skills/recipe-context-engineer/refs/actions/improve.md`](skills/recipe-context-engineer/refs/actions/improve.md) (temp mirror under plugin root → render → copy `.md` back → remove temp).

- If install or run still fails: report **STATIC SKIPPED** with reason — do not silently omit static checks. For render failures, fix JSON (do not invent full markdown).
- The skill does not execute Python — the agent shell runs the script for audit, report render, and write-path gates.

## No pytest in this tree

Regression tests live in the **ai-plugins monorepo** only. Do not run or expect `pytest` inside the installed plugin.

## Product behavior

Skill authors and action procedures: [`skills/recipe-context-engineer/SKILL.md`](skills/recipe-context-engineer/SKILL.md) and `skills/recipe-context-engineer/refs/`.
