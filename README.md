# ai-plugins

Multi-plugin marketplace for **Cursor** and **Claude Code**: context engineering and related agent tooling. Layout follows [Cursor multi-plugin repositories](https://cursor.com/docs/reference/plugins#multi-plugin-repositories) and [Claude Code marketplaces](https://docs.anthropic.com/en/docs/claude-code/plugin-marketplaces).

[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet)](https://claude.ai/code)
[![Unlicense](https://img.shields.io/badge/License-Unlicense-blue.svg)](https://unlicense.org/)
[![Zero Config](https://img.shields.io/badge/setup-zero--config-brightgreen)]()
[![made-with-Markdown](https://img.shields.io/badge/Made%20with-Markdown-1f425f.svg)](http://commonmark.org)
[![Token Efficient](https://img.shields.io/badge/tokens-minimal--overhead-blue)]()
[![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-highlight.svg)](https://sonarcloud.io/summary/new_code?id=rr-agentic-kit_ai-plugins)

## Repository layout

```text
ai-plugins/
├── .cursor-plugin/marketplace.json   # Cursor catalog (repo root)
├── .claude-plugin/marketplace.json   # Claude Code catalog (repo root)
├── pyproject.toml                    # Dev tooling (Python 3.14+, pytest, ruff, mypy)
├── sonar-project.properties          # SonarCloud (CI; set org/key + SONAR_TOKEN)
├── tests/
│   └── context-eng-hero/             # audit_static fixtures, unit, integration
├── plugins/
│   └── context-eng-hero/               # Example plugin (dual runtime)
└── LICENSE                             # Unlicense
```

Root catalogs list plugins under `plugins/<name>/`. Each plugin ships its own `.cursor-plugin/plugin.json` and `.claude-plugin/plugin.json`; shared `skills/`, `commands/`, etc. live inside the plugin directory.

## Install

### Cursor

1. Add this repository as a marketplace source (Git URL or local path), e.g. via [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) or your team’s documented flow for custom marketplaces.
2. Install **context-eng-hero** from the **ai-plugins** marketplace in Cursor settings.

**Local dev**: point the marketplace at this repo’s root so `source: plugins/context-eng-hero` resolves.

### Claude Code

1. Add the marketplace: `/plugin marketplace add <git-url-or-path-to-this-repo-root>`
2. Install the plugin: `/plugin install context-eng-hero@ai-plugins`

**Local dev**: `claude --plugin-dir ./plugins/context-eng-hero` from a checkout (run from repo root and adjust path if needed).

## Usage (quick)

| Runtime | Command |
|---------|---------|
| Cursor | `/context-engineer` (after installing **context-eng-hero**) |
| Claude Code | `/context-eng-hero:context-engineer` |

See `plugins/context-eng-hero/README.md` for component details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, pre-commit, quality gates, tests, CI, SonarCloud, and plugin validation.

When you fork, edit `owner` / `author` placeholders in marketplace and plugin manifests. Add a `repository` URL to plugin manifests once the remote is known.
