"""Unit tests for bump_plugins_version (mocked uv)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from packaging.version import Version

import bump_plugins_version as bump
import validate_plugin_versions as vp


def _install_fake_uv(
    monkeypatch: pytest.MonkeyPatch, new_version: str
) -> list[list[str]]:
    calls: list[list[str]] = []

    def fake_run_uv(args: list[str], *, cwd: Path) -> None:
        calls.append(list(args))
        if args[0] != "version":
            return
        version = new_version if "--bump" in args else args[1]
        (cwd / "pyproject.toml").write_text(
            f'[project]\nname = "test"\nversion = "{version}"\n',
            encoding="utf-8",
        )

    monkeypatch.setattr(bump, "run_uv", fake_run_uv)
    return calls


def _manifest_versions(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): json.loads(path.read_text(encoding="utf-8"))[
            "version"
        ]
        for path in vp.manifest_paths(root)
    }


def test_rejects_unknown_kind():
    with pytest.raises(SystemExit) as exc:
        bump.main(["not-a-kind"])
    assert exc.value.code == 2


def test_accepts_stable_kind():
    assert bump.parse_args(["stable"]).kind == "stable"


def test_write_manifest_preserves_key_order(tmp_path: Path):
    path = tmp_path / "plugin.json"
    path.write_text(
        '{"name": "foo", "version": "1.0.0", "license": "MIT"}\n',
        encoding="utf-8",
    )
    bump.write_manifest_version(path, "2.0.0")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert list(data) == ["name", "version", "license"]
    assert data["version"] == "2.0.0"


def test_increment_local_keeps_plugin_manager_spelling():
    assert bump.increment_local(Version("0.0.4")) == "0.0.4-rc-1"
    assert bump.increment_local(Version("0.0.2-beta-4")) == "0.0.2-beta-5"
    assert bump.increment_local(Version("0.0.2b4")) == "0.0.2-beta-5"
    assert bump.increment_local(Version("0.0.4-rc-1")) == "0.0.4-rc-2"


def test_rc_increments_local_prerelease(mini_repo, monkeypatch, capsys):
    root = mini_repo(
        pyproject_version="0.0.2-beta-4",
        plugins={"foo": "0.0.2-beta-4"},
    )
    monkeypatch.setattr(bump, "REPO_ROOT", root)
    calls: list[list[str]] = []
    monkeypatch.setattr(bump, "run_uv", lambda args, *, cwd: calls.append(list(args)))
    monkeypatch.setattr(bump, "sync_claude_local", lambda _root: 0)

    assert bump.main(["rc"]) == 0

    assert calls == [["lock"]]
    assert vp._read_pyproject_version(root / "pyproject.toml") == "0.0.2-beta-5"
    assert set(_manifest_versions(root).values()) == {"0.0.2-beta-5"}
    out = capsys.readouterr().out
    assert "0.0.2-beta-4 => 0.0.2-beta-5" in out
    assert "0.0.2rc1" not in out
    assert "0.0.2b5" not in out
    assert "  uv.lock" in out


def test_rc_lifts_lagging_then_increments(mini_repo, monkeypatch, capsys):
    root = mini_repo(pyproject_version="0.0.2-beta-4", plugins={"foo": "0.0.1"})
    monkeypatch.setattr(bump, "REPO_ROOT", root)
    calls: list[list[str]] = []
    monkeypatch.setattr(bump, "run_uv", lambda args, *, cwd: calls.append(list(args)))
    monkeypatch.setattr(bump, "sync_claude_local", lambda _root: 0)

    assert bump.main(["rc"]) == 0

    assert calls == [["lock"]]
    assert set(_manifest_versions(root).values()) == {"0.0.2-beta-5"}
    out = capsys.readouterr().out
    assert "plugins/foo/.cursor-plugin/plugin.json: 0.0.1 -> 0.0.2-beta-5" in out
    assert "0.0.2-beta-4 => 0.0.2-beta-5" in out


def test_rc_starts_prerelease_from_stable(mini_repo, monkeypatch, capsys):
    root = mini_repo(pyproject_version="0.0.4", plugins={"foo": "0.0.4"})
    monkeypatch.setattr(bump, "REPO_ROOT", root)
    calls: list[list[str]] = []
    monkeypatch.setattr(bump, "run_uv", lambda args, *, cwd: calls.append(list(args)))
    syncs: list[Path] = []
    monkeypatch.setattr(bump, "sync_claude_local", lambda repo: syncs.append(repo) or 0)

    assert bump.main(["rc"]) == 0

    assert calls == [["lock"]]
    assert vp._read_pyproject_version(root / "pyproject.toml") == "0.0.4-rc-1"
    assert set(_manifest_versions(root).values()) == {"0.0.4-rc-1"}
    assert syncs == [root]
    assert "0.0.4 => 0.0.4-rc-1" in capsys.readouterr().out


def test_rc_propagates_sync_failure(mini_repo, monkeypatch):
    root = mini_repo(pyproject_version="0.0.4", plugins={"foo": "0.0.4"})
    monkeypatch.setattr(bump, "REPO_ROOT", root)
    monkeypatch.setattr(bump, "run_uv", lambda *a, **k: None)
    monkeypatch.setattr(bump, "sync_claude_local", lambda _root: 1)

    assert bump.main(["rc"]) == 1
    assert vp._read_pyproject_version(root / "pyproject.toml") == "0.0.4-rc-1"


def test_patch_does_not_sync_claude(mini_repo, monkeypatch):
    root = mini_repo(pyproject_version="1.0.0", plugins={"foo": "1.0.0"})
    monkeypatch.setattr(bump, "REPO_ROOT", root)
    _install_fake_uv(monkeypatch, "1.0.1")
    monkeypatch.setattr(
        bump, "sync_claude_local", lambda *_a, **_k: pytest.fail("sync must not run")
    )

    assert bump.main(["patch"]) == 0


def test_lagging_plugin_lifted_to_max_then_bumped(mini_repo, monkeypatch, capsys):
    root = mini_repo(pyproject_version="0.0.2", plugins={"foo": "0.0.1"})
    monkeypatch.setattr(bump, "REPO_ROOT", root)
    calls = _install_fake_uv(monkeypatch, "0.0.3")

    assert bump.main(["patch"]) == 0

    assert calls == [
        ["version", "0.0.2", "--frozen"],
        ["version", "--bump", "patch", "--frozen"],
        ["lock"],
    ]
    out = capsys.readouterr().out
    assert "normalize: lifted 2 source(s) to 0.0.2" in out
    assert "plugins/foo/.cursor-plugin/plugin.json: 0.0.1 -> 0.0.2" in out
    assert "plugins/foo/.claude-plugin/plugin.json: 0.0.1 -> 0.0.2" in out
    assert "0.0.2 => 0.0.3" in out
    assert _manifest_versions(root) == {
        "plugins/foo/.cursor-plugin/plugin.json": "0.0.3",
        "plugins/foo/.claude-plugin/plugin.json": "0.0.3",
    }
    assert vp._read_pyproject_version(root / "pyproject.toml") == "0.0.3"


def test_aligned_success_writes_all_manifests(mini_repo, monkeypatch, capsys):
    root = mini_repo(
        pyproject_version="1.0.0",
        plugins={"bar": "1.0.0", "foo": "1.0.0"},
    )
    monkeypatch.setattr(bump, "REPO_ROOT", root)
    calls = _install_fake_uv(monkeypatch, "1.1.0")

    assert bump.main(["minor"]) == 0

    assert calls == [
        ["version", "1.0.0", "--frozen"],
        ["version", "--bump", "minor", "--frozen"],
        ["lock"],
    ]
    out = capsys.readouterr().out
    assert "normalize: already at 1.0.0" in out
    assert "1.0.0 => 1.1.0" in out
    versions = _manifest_versions(root)
    assert versions == {
        "plugins/bar/.cursor-plugin/plugin.json": "1.1.0",
        "plugins/bar/.claude-plugin/plugin.json": "1.1.0",
        "plugins/foo/.cursor-plugin/plugin.json": "1.1.0",
        "plugins/foo/.claude-plugin/plugin.json": "1.1.0",
    }
    for rel in versions:
        assert f"  {rel}" in out
    assert "  pyproject.toml" in out
    assert "  uv.lock" in out


def test_invalid_pep440_fails_before_uv(mini_repo, monkeypatch):
    root = mini_repo(pyproject_version="not-a-version", plugins={"foo": "1.0.0"})
    monkeypatch.setattr(bump, "run_uv", lambda *a, **k: pytest.fail("uv must not run"))
    with pytest.raises(SystemExit, match="invalid PEP 440 version"):
        bump.run_bump("patch", root)


def test_canonicalizes_pep440_spelling(mini_repo, monkeypatch, capsys):
    root = mini_repo(
        pyproject_version="0.0.2-beta-4",
        plugins={"foo": "0.0.2b4"},
    )
    monkeypatch.setattr(bump, "REPO_ROOT", root)
    calls = _install_fake_uv(monkeypatch, "0.0.3")

    assert bump.main(["patch"]) == 0
    assert calls[0] == ["version", "0.0.2b4", "--frozen"]
    assert calls[-1] == ["lock"]
    out = capsys.readouterr().out
    assert "normalize: canonicalized to 0.0.2b4" in out
    assert "  uv.lock" in out
