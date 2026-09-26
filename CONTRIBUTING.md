# Contributing to ai-plugins

Development tooling applies to the **monorepo checkout** only. Installed plugins (`plugins/<name>/`) do not include `tests/`, root `pyproject.toml`, or CI configs.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- **Python 3.14**
- [lefthook](https://lefthook.dev/) (e.g. `brew install lefthook`)
- [actionlint](https://github.com/rhysd/actionlint) (e.g. `brew install actionlint`) — runs when staging `.github/workflows/*`

## Setup

From the repository root:

```bash
uv sync --all-groups
lefthook install
```

Non-merge commits run the quality jobs in [`lefthook.yml`](lefthook.yml). Skip with `LEFTHOOK=0` or `git commit --no-verify`.

First-time baseline (optional, matches CI lint/format/type/security hooks):

```bash
lefthook run pre-commit --all-files
```

## Quality checks (local)

Same commands as [`.github/workflows/python-quality.yml`](.github/workflows/python-quality.yml):

```bash
uv run ruff check plugins/context-eng-hero/scripts plugins/rrraw/scripts scripts tests/context-eng-hero tests/rrraw tests/scripts
uv run black --check plugins/context-eng-hero/scripts plugins/rrraw/scripts scripts tests/context-eng-hero tests/rrraw tests/scripts
uv run mypy
uv run bandit -r plugins/context-eng-hero/scripts plugins/rrraw/scripts -c pyproject.toml
uv export --frozen --format requirements.txt -o /tmp/requirements.txt
uv run pip-audit -r /tmp/requirements.txt
```

Format/fix locally:

```bash
uv run ruff check --fix plugins/context-eng-hero/scripts plugins/rrraw/scripts scripts tests/context-eng-hero tests/rrraw tests/scripts
uv run black plugins/context-eng-hero/scripts plugins/rrraw/scripts scripts tests/context-eng-hero tests/rrraw tests/scripts
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
  --cov=plugins/context-eng-hero/scripts \
  --cov=plugins/rrraw/scripts \
  --cov=scripts \
  --cov-report=term-missing \
  --cov-report=xml
```

## CI

[`.github/workflows/python-quality.yml`](.github/workflows/python-quality.yml) runs Ruff, Black, Mypy, Bandit, pip-audit, pytest with `coverage.xml`, and SonarCloud on pull requests and pushes to `master`, `release/**`, and `hotfix/**`. PRs into `master` must come from `release/**` or `hotfix/**` (enforced by the `pr-base-guard` job).

Release versioning is owned by [`.github/workflows/release-control.yml`](.github/workflows/release-control.yml): merges into an active `release/X.Y.0` tick the RC; promoting `release/X.Y.0` → `master` graduates to stable, tags, creates a GitHub Release, and opens `release/X.(Y+1).0` at `-rc1`. Hotfixes merge `hotfix/X.Y.Z` → `master` and ship patch `X.Y.Z`. See **Release branches** below.

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

`pyproject.toml` `[project].version` and each plugin’s `.cursor-plugin/plugin.json` and `.claude-plugin/plugin.json` `version` fields must match. CI and lefthook run:

```bash
uv run python scripts/validate_plugin_versions.py
```

Lockstep bump (lifts every plugin to the PEP 440 max, then increments):

```bash
uv run python scripts/bump_plugins_version.py {major|minor|patch|rc|stable}
```

RC strings use `{base}-rc{N}` (for example `0.1.0-rc1`, not `0.1.0-rc-1`). CI sets `BUMP_SKIP_INSTALL=1`; local `rc` still runs `install_claude_local` unless you pass `--no-install`. Manual bumps are for recovery only — routine RC ticks and stable graduation run in CI.

## Release branches

**PR base policy (hard):**

| Head branch | PR base | Effect |
|-------------|---------|--------|
| Work branches (`feat/`, `chore/`, `fix/`, `bug/`, `docs/`, …) | Active `release/X.Y.0` | Merge ticks RC on the release branch |
| `release/X.Y.0` | `master` | Promote when the train is done |
| `hotfix/X.Y.Z` | `master` | Patch release from branch name |

Do not open work PRs into `master`. After the first train is seeded, there is always an active `release/*`; promoting `release/X.Y.0` auto-opens the next minor `release/X.(Y+1).0` at `-rc1`. Major trains (`release/1.0.0`, etc.) are opened only via `workflow_dispatch` on `release-control` with `action=open`.

**One-time migration:** create `release/0.1.0` from current `master`; CI sets `0.1.0-rc1`. The abandoned `0.0.6-rc-*` line on `master` is not shipped.

**Recovery / dispatch:**

Maintainer path (dispatches `.github/workflows/release-control.yml` via `gh`):

```bash
just release active
just release open
just release rc
just release promote
just release hotfix hotfix/0.1.1
just release seed 0.2.0 --yes
just branch-new feat/foo --base release/0.1.0
just create-pr --title "…" --description "…"
```

CI path (version bumps inside the workflow checkout):

```bash
just ci-release {open|rc|promote|hotfix|next-minor} --branch release/0.1.0
```

Or trigger the `release-control` workflow manually. Bot pushes use secret `RELEASE_BOT_TOKEN` when branch protection requires bypass; otherwise `GITHUB_TOKEN`.

## Plugin validation

From repo root:

```bash
claude plugin validate .
claude plugin validate ./plugins/context-eng-hero
```

## Fork notes

Edit `owner` / `author` placeholders in marketplace and plugin manifests when you fork. Add a `repository` URL to plugin manifests once the remote is known.

Fork PRs do not require maintainer **review** approval to merge upstream — quality gates are CI status checks (`quality`, `sonarcloud`) plus CodeQL/code-quality rules on `master`. External contributors **do** need maintainer approval to **run** GitHub Actions on fork PRs (repo setting: all external contributors).
