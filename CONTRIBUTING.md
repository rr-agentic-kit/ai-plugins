# Contributing to ai-plugins

Development tooling applies to the **monorepo checkout** only. Installed plugins (`plugins/<name>/`) do not include `tests/`, root `pyproject.toml`, or CI configs.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- **Python 3.14**

## Setup

From the repository root:

```bash
uv sync --all-groups
uv run pre-commit install
```

First-time baseline (optional, matches CI lint/format/type/security hooks):

```bash
uv run pre-commit run --all-files
```

## Quality checks (local)

Same commands as [`.github/workflows/python-quality.yml`](.github/workflows/python-quality.yml):

```bash
uv run ruff check plugins/context-eng-hero/scripts plugins/rrraw/scripts tests/context-eng-hero tests/rrraw
uv run black --check plugins/context-eng-hero/scripts plugins/rrraw/scripts tests/context-eng-hero tests/rrraw
uv run mypy
uv run bandit -r plugins/context-eng-hero/scripts plugins/rrraw/scripts -c pyproject.toml
uv export --frozen --format requirements.txt -o /tmp/requirements.txt
uv run pip-audit -r /tmp/requirements.txt
```

Format/fix locally:

```bash
uv run ruff check --fix plugins/context-eng-hero/scripts plugins/rrraw/scripts tests/context-eng-hero tests/rrraw
uv run black plugins/context-eng-hero/scripts plugins/rrraw/scripts tests/context-eng-hero tests/rrraw
```

## Tests

Full suite (all plugins):

```bash
uv run pytest tests/ -v
```

Single plugin:

```bash
uv run pytest tests/context-eng-hero/ -v
uv run pytest tests/rrraw/ -v
```

Coverage (matches CI + SonarCloud):

```bash
uv run pytest tests/ -v \
  --cov=plugins/context-eng-hero/scripts/audit_static \
  --cov=plugins/rrraw/scripts/validate_planning_script \
  --cov-report=term-missing \
  --cov-report=xml
```

## CI

[`.github/workflows/python-quality.yml`](.github/workflows/python-quality.yml) runs Ruff, Black, Mypy, Bandit, pip-audit, pytest with `coverage.xml`, and SonarCloud on pull requests and pushes to `main`.

### SonarCloud (one-time setup)

1. Import this repository at [sonarcloud.io](https://sonarcloud.io) (GitHub App).
2. Set `sonar.organization` and `sonar.projectKey` in [`sonar-project.properties`](sonar-project.properties) to match the SonarCloud project.
3. Add repository secret **`SONAR_TOKEN`** (SonarCloud → My Account → Security).
4. Disable **Automatic Analysis** if you only want CI-driven scans (recommended for this layout).

Until `SONAR_TOKEN` and placeholders are configured, the `sonarcloud` job will fail; other quality jobs still run.

## Running the static audit script (dev convenience)

From a monorepo checkout, after `uv sync`:

```bash
cd plugins/context-eng-hero
uv run --project ../.. python scripts/audit_static.py . skills/recipe-context-engineer/SKILL.md
```

End users and agents inside the **installed plugin** use plugin-only bootstrap — see `plugins/context-eng-hero/CLAUDE.md` **Python runtime**.

## Version alignment

`pyproject.toml` `[project].version` and each plugin’s `.cursor-plugin/plugin.json` and `.claude-plugin/plugin.json` `version` fields must match. CI and pre-commit run:

```bash
uv run python scripts/validate_plugin_versions.py
```

Lockstep bump (lifts every plugin to the PEP 440 max, then increments):

```bash
uv run python scripts/bump_plugins_version.py {major|minor|patch|rc}
```

`rc` ticks the local prerelease (`0.0.2-beta-4` → `0.0.2-beta-5`) so Claude Code / Cursor cache a new version — required before `install_claude_local` or any plugin-manager update. `stable` graduates a prerelease (`0.0.2-beta-4` → `0.0.2`); `patch` does not (`0.0.2-beta-4` → `0.0.3`). Re-run the validator after a bump.

## Plugin validation

From repo root:

```bash
claude plugin validate .
claude plugin validate ./plugins/context-eng-hero
```

## Fork notes

Edit `owner` / `author` placeholders in marketplace and plugin manifests when you fork. Add a `repository` URL to plugin manifests once the remote is known.

Fork PRs do not require maintainer **review** approval to merge upstream — quality gates are CI status checks (`quality`, `sonarcloud`) plus CodeQL/code-quality rules on `master`. External contributors **do** need maintainer approval to **run** GitHub Actions on fork PRs (repo setting: all external contributors).
