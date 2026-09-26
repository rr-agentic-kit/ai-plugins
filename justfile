release *ARGS:
    uv run python scripts/release.py {{ARGS}}

branch-new *ARGS:
    uv run python scripts/branch_new.py {{ARGS}}

create-pr *ARGS:
    uv run python scripts/create_pr.py {{ARGS}}

validate-versions:
    uv run python scripts/validate_plugin_versions.py

bump kind:
    uv run python scripts/bump_plugins_version.py {{kind}}

install-claude:
    uv run python scripts/install_claude_local.py

ci-release *ARGS:
    uv run python scripts/ci_release_control.py {{ARGS}}

test-scripts *ARGS:
    uv run pytest tests/scripts/ {{ARGS}}
