# ai-plugins — monorepo agent contract

Dual-runtime plugin marketplace (Cursor + Claude Code). Plugins live under `plugins/` and are listed in root `.cursor-plugin/marketplace.json` and `.claude-plugin/marketplace.json`.

## Repository layout

- `plugins/<name>/` — self-contained plugin (skills, commands, manifests)
- `.cursor-plugin/marketplace.json` / `.claude-plugin/marketplace.json` — catalogs at repo root
- `tests/<plugin>/` — monorepo only; not shipped in marketplace installs
- `pyproject.toml` — dev tooling at repo root only (uv, pytest, ruff, mypy)
- `scripts/validate_plugin_versions.py` — version alignment check (CI and pre-commit)
- `scripts/bump_plugins_version.py` — lockstep version bump across pyproject + all plugin manifests

## Hard rules

- Plugins are **self-contained** under `plugins/`. Do not reference paths outside `plugins/` in plugin markdown unless documenting an explicit cross-plugin dependency.
- Plugin Python scripts must have tests in `tests/<plugin>/`. Tests are not part of the install artifact; they run in this monorepo and CI only.
- **Version alignment:** `pyproject.toml` `[project].version` must match each plugin’s `.cursor-plugin/plugin.json` and `.claude-plugin/plugin.json` `version` fields. Run `uv run python scripts/validate_plugin_versions.py` from repo root before committing manifest or version bumps.
- **Monorepo vs install:** When working inside `plugins/<name>/` as an installed artifact, do not assume `tests/`, repo-root `pyproject.toml`, `uv.lock`, or `../../` exist. In a full monorepo checkout, those paths are available at the repo root—use this file and `CONTRIBUTING.md`, not plugin `CLAUDE.md`, for maintainer workflows.

## Tech stack

- Python **3.14+** (`requires-python` in `pyproject.toml`)
- Dev environment: **uv** from repository root (`uv sync --all-groups`)

## Common commands (repo root)

Run from the repository root unless noted.

```bash
uv sync --all-groups
uv run pytest tests/ -v
uv run ruff check plugins/context-eng-hero/scripts plugins/rrraw/scripts scripts tests/context-eng-hero tests/rrraw tests/scripts
uv run python scripts/validate_plugin_versions.py
uv run python scripts/install_claude_local.py
uv run python scripts/bump_plugins_version.py {major|minor|patch|rc}  # rc also runs install_claude_local
claude plugin validate .
claude plugin validate ./plugins/context-eng-hero
```

Full quality matrix (Black, Mypy, Bandit, pip-audit, coverage, Sonar): see `CONTRIBUTING.md`.

## Testing

- Full suite: `uv run pytest tests/ -v`
- Single plugin: `uv run pytest tests/context-eng-hero/ -v` or `uv run pytest tests/rrraw/ -v`
- Repo-root scripts: `uv run pytest tests/scripts/ -v`
- Coverage + CI parity: `CONTRIBUTING.md`
- Production scripts: `plugins/*/scripts/**/*.py`, repo-root `scripts/*.py`
- Tests live only under `tests/<plugin>/` or `tests/scripts/` — never under `plugins/`
- Coverage omit: `*/__main__.py` (entry shims; exercised via subprocess smoke tests)
- Subprocess CLI tests do not attribute coverage; use direct `main()` unit tests for CLI modules

## Safety

- Never put secrets, tokens, or credentials in `CLAUDE.md`, plugin markdown, or commits
- Personal overrides only in gitignored `CLAUDE.local.md` at repo root
- Do not run destructive git (`push --force`, hard reset) unless the user explicitly requests it
- Marketplace-install context: treat paths outside the plugin tree as unavailable (see Hard rules)

## Where to look next

| Working on… | Read first |
|-------------|------------|
| Plugin runtime / static audit / PyYAML bootstrap | `plugins/context-eng-hero/CLAUDE.md` |
| Authoring skills, commands, rubrics | `plugins/context-eng-hero/skills/recipe-context-engineer/SKILL.md` |
| CI, pre-commit, Sonar, fork setup | `CONTRIBUTING.md` |
| Install / marketplace usage | `README.md` |

## Plugin-specific work

For **context-eng-hero** authoring, audit gates, or `audit_static.py`: use `plugins/context-eng-hero/CLAUDE.md` for Python bootstrap and invocation. Do not duplicate those command blocks here.

## Non-goals for this file

- Per-plugin feature documentation (use each plugin’s `README.md`)
- Long rubrics or pre-ship checklists (use `skills/recipe-context-engineer/refs/` inside the plugin)
- Personal preferences (use gitignored `CLAUDE.local.md` at repo root if needed)
- Tone / role / communication: use user-global `~/.claude/CLAUDE.md` — do not duplicate here

## Conventions

- Skill prefixes: `recipe-*` (context-eng-hero, jobseeker); `rr-*` (rrraw discovery/planner/test)
- Commands sub-divisions:
    - `-fix` focuses on adjusting wrong behavior based on previous assessment/review or human input
    - `-design|add|create` for start something new
