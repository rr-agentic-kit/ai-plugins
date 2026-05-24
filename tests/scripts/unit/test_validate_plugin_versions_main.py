"""Unit tests for validate_plugin_versions (mocked main paths)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from conftest import m


def test_main_returns_0_when_aligned(capsys):
    with patch.object(
        m,
        "collect_versions",
        return_value={"a": "1.0.0", "b": "1.0.0"},
    ):
        assert m.main() == 0
    out = capsys.readouterr()
    assert "version alignment ok: 1.0.0" in out.out


def test_main_returns_1_on_mismatch(capsys):
    with patch.object(
        m,
        "collect_versions",
        return_value={
            "pyproject.toml [project].version": "1.0.0",
            "plugins/foo/.cursor-plugin/plugin.json": "2.0.0",
        },
    ):
        assert m.main() == 1
    err = capsys.readouterr().err
    assert "version mismatch" in err
    assert "pyproject.toml [project].version: 1.0.0" in err
    assert "plugins/foo/.cursor-plugin/plugin.json: 2.0.0" in err
    assert "expected one version, found: 1.0.0, 2.0.0" in err


def test_main_returns_1_on_json_decode_error(capsys):
    with patch.object(
        m,
        "collect_versions",
        side_effect=json.JSONDecodeError("msg", "doc", 0),
    ):
        assert m.main() == 1
    assert "validate_plugin_versions:" in capsys.readouterr().err


def test_main_returns_1_on_value_error(capsys):
    with patch.object(
        m,
        "collect_versions",
        side_effect=ValueError("missing version in foo"),
    ):
        assert m.main() == 1
    assert "validate_plugin_versions: missing version in foo" in capsys.readouterr().err


def test_read_manifest_version_missing_key(tmp_path: Path):
    manifest = tmp_path / "plugin.json"
    manifest.write_text('{"name": "foo"}', encoding="utf-8")
    with pytest.raises(ValueError, match="missing version"):
        m._read_manifest_version(manifest)


def test_read_pyproject_version_missing_key(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "x"\n', encoding="utf-8")
    with pytest.raises(ValueError, match=r"missing \[project\]\.version"):
        m._read_pyproject_version(pyproject)
