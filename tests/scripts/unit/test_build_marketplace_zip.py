"""Unit tests for build_marketplace_zip."""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

import pytest

import build_marketplace_zip as bmz


def _write_marketplace(root: Path, plugin_names: list[str]) -> None:
    catalog = {
        "name": "ai-plugins",
        "plugins": [{"name": n, "source": f"plugins/{n}"} for n in plugin_names],
    }
    for sub in (".cursor-plugin", ".claude-plugin"):
        path = root / sub / "marketplace.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(catalog), encoding="utf-8")


def _mini_release_repo(tmp_path: Path, *, version: str = "1.2.3") -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    root.joinpath("pyproject.toml").write_text(
        f'[project]\nname = "test"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    root.joinpath("README.md").write_text("# test\n", encoding="utf-8")
    root.joinpath("tests").mkdir()
    root.joinpath("tests", "noise.py").write_text("x = 1\n", encoding="utf-8")
    _write_marketplace(root, ["alpha", "beta"])
    for name in ("alpha", "beta"):
        plugin = root / "plugins" / name
        plugin.mkdir(parents=True)
        manifest = plugin / ".cursor-plugin" / "plugin.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps({"name": name, "version": version}),
            encoding="utf-8",
        )
        (plugin / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    return root


def test_zip_output_name_and_top_dir():
    assert bmz.zip_output_name("0.0.6-rc-27") == "ai-plugins-0.0.6-rc-27.zip"
    assert bmz.zip_archive_top_dir("1.0.0") == "ai-plugins-1.0.0"


def test_is_prerelease_version():
    assert bmz.is_prerelease_version("0.0.6-rc-27") is True
    assert bmz.is_prerelease_version("1.0.0") is False


def test_release_staging_paths_excludes_tests_and_lists_plugins(tmp_path: Path):
    root = _mini_release_repo(tmp_path)
    rels = {p.as_posix() for p in bmz.release_staging_paths(root)}
    assert "README.md" in rels
    assert "plugins/alpha/SKILL.md" in rels
    assert not any(p.startswith("tests/") for p in rels)
    assert bmz.catalog_plugin_names(root) == ["alpha", "beta"]


def test_build_marketplace_zip_contents(tmp_path: Path):
    root = _mini_release_repo(tmp_path, version="2.0.0")
    out = tmp_path / "dist"
    archive = bmz.build_marketplace_zip(root, out)
    assert archive.name == "ai-plugins-2.0.0.zip"
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
    assert "ai-plugins-2.0.0/README.md" in names
    assert "ai-plugins-2.0.0/plugins/alpha/SKILL.md" in names
    assert not any(n.startswith("ai-plugins-2.0.0/tests/") for n in names)


def test_build_marketplace_zip_matches_catalog_on_real_repo(repo_root: Path):
    catalog = bmz.catalog_plugin_names(repo_root)
    plugin_tops = {
        p.parts[1]
        for p in bmz.release_staging_paths(repo_root)
        if len(p.parts) >= 2
        and p.parts[0] == "plugins"
        and (repo_root / "plugins" / p.parts[1]).is_dir()
    }
    assert plugin_tops == set(catalog)


def test_build_marketplace_zip_real_repo_excludes_monorepo_tests(repo_root: Path):
    version = bmz.read_pyproject_version(repo_root / "pyproject.toml")
    top = bmz.zip_archive_top_dir(version)
    out = repo_root / "dist" / "pytest-artifact"
    archive = bmz.build_marketplace_zip(repo_root, out)
    with zipfile.ZipFile(archive) as zf:
        assert not any(name.startswith(f"{top}/tests/") for name in zf.namelist())
    archive.unlink()


def test_catalog_plugin_missing_dir_raises(tmp_path: Path):
    root = _mini_release_repo(tmp_path)
    shutil.rmtree(root / "plugins" / "alpha")
    with pytest.raises(FileNotFoundError, match="plugins/alpha"):
        bmz.release_staging_paths(root)
