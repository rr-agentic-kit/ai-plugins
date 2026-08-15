"""Integration tests for validate_plugin_versions (real filesystem trees)."""

from __future__ import annotations

import tomllib

import pytest
from conftest import REPO_ROOT, m


def test_manifest_paths_lists_both_runtimes(mini_repo):
    root = mini_repo(plugins={"bar": "1.0.0", "foo": "1.0.0"})
    rels = [p.relative_to(root).as_posix() for p in m.manifest_paths(root)]
    assert rels == [
        "plugins/bar/.cursor-plugin/plugin.json",
        "plugins/bar/.claude-plugin/plugin.json",
        "plugins/foo/.cursor-plugin/plugin.json",
        "plugins/foo/.claude-plugin/plugin.json",
    ]


def test_collect_versions_aligned(mini_repo):
    root = mini_repo(pyproject_version="0.2.0", plugins={"foo": "0.2.0"})
    versions = m.collect_versions(root)
    assert set(versions.values()) == {"0.2.0"}
    assert len(versions) == 3


def test_collect_versions_mismatch_via_main(mini_repo, monkeypatch):
    root = mini_repo(
        pyproject_version="0.1.0",
        plugins={"foo": {"cursor": "0.2.0", "claude": "0.1.0"}},
    )
    monkeypatch.setattr(m, "REPO_ROOT", root)
    assert m.main() == 1


def test_collect_versions_missing_manifest(mini_repo):
    root = mini_repo(
        plugins={"foo": "1.0.0"},
        omit_manifest=("foo", ".claude-plugin/plugin.json"),
    )
    with pytest.raises(SystemExit, match="missing manifest"):
        m.collect_versions(root)


def test_collect_versions_missing_plugins_dir(mini_repo):
    root = mini_repo(skip_plugins_dir=True)
    with pytest.raises(SystemExit, match="plugins directory not found"):
        m.collect_versions(root)


def test_golden_repo_versions_align():
    versions = m.collect_versions(REPO_ROOT)
    unique = set(versions.values())
    assert len(unique) == 1

    pyproject = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    expected = data["project"]["version"]
    assert unique == {expected}
