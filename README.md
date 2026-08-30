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
│   ├── context-eng-hero/             # audit_static fixtures, unit, integration
│   ├── rrraw/                        # validate_planning / rr-test unit tests
│   └── scripts/                      # monorepo script unit/integration tests
├── plugins/
│   ├── context-eng-hero/             # Context engineering (dual runtime)
│   ├── rrraw/                        # Test excellence + planning (dual runtime)
│   └── jobseeker/                    # Resume / cover-letter coaching (dual runtime)
└── LICENSE                             # Unlicense
```

Root catalogs list plugins under `plugins/<name>/`. Each plugin ships its own `.cursor-plugin/plugin.json` and `.claude-plugin/plugin.json`; shared `skills/`, `commands/`, etc. live inside the plugin directory.

## Install

End-user and agent install steps live in **[INSTALL.md](INSTALL.md)** (human) and **[INSTALL-AI.md](INSTALL-AI.md)** (agent runbook). Summary: Claude Code uses `/plugin marketplace add rr-agentic-kit/ai-plugins` then `/plugin install <name>@ai-plugins`; Cursor copies plugins into `~/.cursor/plugins/local/` (see INSTALL.md). Monorepo Claude shortcut: `uv run python scripts/install_claude_local.py`.

## Usage (quick)

| Runtime | Command |
|---------|---------|
| Cursor | `/context-engineer` (after installing **context-eng-hero**) |
| Claude Code | `/context-eng-hero:context-engineer` |

See each plugin’s `README.md` under `plugins/` for component details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, pre-commit, quality gates, tests, CI, SonarCloud, and plugin validation.

When you fork, edit `owner` / `author` placeholders in marketplace and plugin manifests. Add a `repository` URL to plugin manifests once the remote is known.
