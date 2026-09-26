# ai-plugins — monorepo agent contract

Dual-runtime plugin marketplace (Cursor + Claude Code). Plugins live under `plugins/` and are listed in root `.cursor-plugin/marketplace.json` and `.claude-plugin/marketplace.json`.

## Hard rules

- Plugins are **self-contained** under `plugins/`. Do not reference paths outside `plugins/` in plugin markdown unless documenting an explicit cross-plugin dependency.
- Plugin Python scripts must have tests in `tests/<plugin>/`. Tests are not part of the install artifact; they run in this monorepo and CI only. Tests live only under `tests/<plugin>/` or `tests/scripts/` — never under `plugins/`.
- **Version alignment:** `pyproject.toml` `[project].version` must match each plugin’s `.cursor-plugin/plugin.json` and `.claude-plugin/plugin.json` `version` fields. Run `uv run python scripts/validate_plugin_versions.py` from repo root before committing manifest or version bumps.
- **Release-target PRs:** Open work (`feat/`, `chore/`, `fix/`, …) against the active `release/X.Y.0`, not `master`. Only `release/**` and `hotfix/**` merge to `master`. CI owns RC ticks and stable graduation via `scripts/ci_release_control.py` / `.github/workflows/release-control.yml`; manual `bump_plugins_version.py` is recovery-only (`--no-install` in CI).
- **Monorepo vs install:** When working inside `plugins/<name>/` as an installed artifact, do not assume `tests/`, repo-root `pyproject.toml`, `uv.lock`, or `../../` exist. In a full monorepo checkout, those paths are available at the repo root—use this file and `CONTRIBUTING.md`, not plugin `CLAUDE.md`, for maintainer workflows.
- **Dual-runtime parity:** Prefer full Cursor + Claude Code parity for skills, commands, agents, hooks, scripts, and both `plugin.json` manifests. If a capability is runtime-specific, document the gap in the plugin README and leave a tracked follow-up — do not silently ship one-runtime-only behavior for marketplace plugins.

## Tech stack

- Python **3.14+** (`requires-python` in `pyproject.toml`)
- Dev environment: **uv** from repository root (`uv sync --all-groups`)

## Essential commands (repo root)

```bash
uv sync --all-groups
just test-scripts -v
uv run pytest tests/context-eng-hero/ -v   # or tests/rrraw/
uv run ruff check plugins/context-eng-hero/scripts plugins/rrraw/scripts scripts tests/context-eng-hero tests/rrraw tests/scripts
just validate-versions
just install-claude
just bump {major|minor|patch|rc|stable}  # rc runs install_claude_local unless --no-install / BUMP_SKIP_INSTALL=1
just release active
just release open
just branch-new feat/foo --base release/0.1.0
just create-pr --title "…" --description "…"
just ci-release {open|rc|promote|hotfix|next-minor} --branch release/X.Y.0
claude plugin validate .
claude plugin validate ./plugins/context-eng-hero
```

Equivalent one-liners use `uv run python scripts/<script>.py` when `just` is unavailable.

Full quality matrix (Black, Mypy, Bandit, pip-audit, coverage, Sonar): see `CONTRIBUTING.md`.

## Safety

- Never put secrets, tokens, or credentials in `AGENTS.md`, `CLAUDE.md`, plugin markdown, or commits
- Personal overrides only in gitignored `.agents/local.md`
- Do not run destructive git (`push --force`, hard reset) unless the user explicitly requests it
- Marketplace-install context: treat paths outside the plugin tree as unavailable (see Hard rules)

## Where to look

| Working on… | Read first |
|-------------|------------|
| Plugin runtime / static audit / PyYAML bootstrap | `plugins/context-eng-hero/CLAUDE.md` |
| Authoring skills, commands, rubrics | `plugins/context-eng-hero/skills/recipe-context-engineer/SKILL.md` |
| Static memory / AGENTS packs | `plugins/context-eng-hero/skills/recipe-static-memory/SKILL.md` |
| Dual-runtime plugin hooks (Cursor + Claude) | `.agents/hooks.md` |
| CI, lefthook, Sonar, fork setup | `CONTRIBUTING.md` |
| Install / marketplace usage | `README.md` |
| Per-plugin features | that plugin’s `README.md` |

## Conventions

- Skill prefixes: `recipe-*` (context-eng-hero, jobseeker); rrraw public `rr-*` (discovery/planner/builder); manual specialists `s-*`
- Commands sub-divisions:
  - `-fix` focuses on adjusting wrong behavior based on previous assessment/review or human input
  - `-design|add|create` for start something new
- Layout shortcuts: `plugins/<name>/` (shipped), `tests/<plugin>/` (monorepo only), root catalogs `.cursor-plugin/marketplace.json` / `.claude-plugin/marketplace.json`

## Non-goals for this file

- Per-plugin feature documentation (plugin `README.md`)
- Long rubrics or pre-ship checklists (`skills/recipe-context-engineer/refs/` inside the plugin)
- Full contributor quality/coverage procedures (`CONTRIBUTING.md`)
- Personal preferences (gitignored `.agents/local.md`)
- Tone / role / communication (user-global `~/.claude/CLAUDE.md`)
