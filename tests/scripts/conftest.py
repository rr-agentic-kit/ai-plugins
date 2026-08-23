"""Shared fixtures for repo script tests."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
import install_claude_local as icl  # noqa: E402
import validate_plugin_versions as m  # noqa: E402


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def validate_module():
    return m


@pytest.fixture
def install_module():
    return icl


PluginVersions = dict[str, str | dict[str, str]]


@pytest.fixture
def mini_repo(tmp_path: Path) -> Callable[..., Path]:
    """Build a minimal repo tree with pyproject.toml and plugin manifests."""

    def _build(
        *,
        pyproject_version: str = "1.0.0",
        plugins: PluginVersions | None = None,
        omit_manifest: tuple[str, str] | None = None,
        skip_plugins_dir: bool = False,
    ) -> Path:
        root = tmp_path / "repo"
        root.mkdir()
        root.joinpath("pyproject.toml").write_text(
            f'[project]\nname = "test"\nversion = "{pyproject_version}"\n',
            encoding="utf-8",
        )
        if skip_plugins_dir:
            return root

        plugins_dir = root / "plugins"
        plugins_dir.mkdir()
        plugin_specs = plugins if plugins is not None else {"foo": "1.0.0"}

        for name, spec in plugin_specs.items():
            plugin_dir = plugins_dir / name
            plugin_dir.mkdir()
            if isinstance(spec, str):
                cursor_v = claude_v = spec
            else:
                cursor_v = spec.get("cursor", pyproject_version)
                claude_v = spec.get("claude", pyproject_version)

            manifests: list[tuple[str, str]] = [
                (".cursor-plugin/plugin.json", cursor_v),
                (".claude-plugin/plugin.json", claude_v),
            ]
            for rel, version in manifests:
                if omit_manifest == (name, rel):
                    continue
                path = plugin_dir / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps({"name": name, "version": version}),
                    encoding="utf-8",
                )
        return root

    return _build
