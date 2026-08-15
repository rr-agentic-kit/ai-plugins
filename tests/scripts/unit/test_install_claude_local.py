"""Unit tests for install_claude_local (mocked Claude CLI)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import icl


def _write_catalog(
    root: Path,
    *,
    name: str = "ai-plugins",
    plugins: list[str] | None = None,
) -> Path:
    catalog_dir = root / ".claude-plugin"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "name": name,
        "plugins": [
            {"name": plugin, "source": f"./plugins/{plugin}"}
            for plugin in (plugins if plugins is not None else ["foo", "bar"])
        ],
    }
    (catalog_dir / "marketplace.json").write_text(json.dumps(payload), encoding="utf-8")
    return root


class FakeClaude:
    def __init__(
        self,
        *,
        marketplaces: list[dict] | dict | None = None,
        plugins: list[dict] | dict | str | None = None,
        fail_specs: frozenset[str] | None = None,
    ) -> None:
        self.marketplaces = [] if marketplaces is None else marketplaces
        self.plugins = [] if plugins is None else plugins
        self.fail_specs = fail_specs or frozenset()
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str]) -> str:
        self.calls.append(args)
        if args[:3] == ["plugin", "marketplace", "list"]:
            return (
                self.marketplaces
                if isinstance(self.marketplaces, str)
                else json.dumps(self.marketplaces)
            )
        if args[:2] == ["plugin", "list"] and "--json" in args:
            return (
                self.plugins
                if isinstance(self.plugins, str)
                else json.dumps(self.plugins)
            )
        if args[:3] == ["plugin", "marketplace", "remove"]:
            name = args[3]
            if isinstance(self.marketplaces, list):
                self.marketplaces = [
                    entry for entry in self.marketplaces if entry.get("name") != name
                ]
            self.plugins = []
            return ""
        spec = args[2] if len(args) > 2 else ""
        if spec in self.fail_specs:
            raise icl.ClaudeCommandError(args, 1, f"failed {spec}")
        return "ok"

    def command_heads(self) -> list[tuple[str, ...]]:
        heads: list[tuple[str, ...]] = []
        for args in self.calls:
            if args[:3] == ["plugin", "marketplace", "list"]:
                heads.append(("marketplace", "list"))
            elif args[:3] == ["plugin", "marketplace", "remove"]:
                heads.append(("marketplace", "remove", args[3]))
            elif args[:3] == ["plugin", "marketplace", "add"]:
                heads.append(("marketplace", "add", args[3]))
            elif args[:2] == ["plugin", "list"]:
                heads.append(("plugin", "list"))
            elif args[:2] == ["plugin", "install"]:
                heads.append(("plugin", "install", args[2]))
            elif args[:2] == ["plugin", "update"]:
                heads.append(("plugin", "update", args[2]))
        return heads


def test_github_marketplace_is_removed_then_added(tmp_path: Path):
    root = _write_catalog(tmp_path)
    fake = FakeClaude(
        marketplaces=[
            {"name": "ai-plugins", "source": "github", "repo": "org/ai-plugins"}
        ]
    )
    assert icl.main(repo_root=root, run=fake) == 0
    assert fake.command_heads() == [
        ("marketplace", "list"),
        ("marketplace", "remove", "ai-plugins"),
        ("marketplace", "add", str(root)),
        ("plugin", "list"),
        ("plugin", "install", "foo@ai-plugins"),
        ("plugin", "install", "bar@ai-plugins"),
    ]


def test_local_same_path_skips_marketplace(tmp_path: Path):
    root = _write_catalog(tmp_path)
    fake = FakeClaude(
        marketplaces=[
            {
                "name": "ai-plugins",
                "source": "directory",
                "path": str(root),
            }
        ]
    )
    assert icl.main(repo_root=root, run=fake) == 0
    heads = fake.command_heads()
    assert ("marketplace", "remove", "ai-plugins") not in heads
    assert not any(h[:2] == ("marketplace", "add") for h in heads)
    assert ("plugin", "install", "foo@ai-plugins") in heads


def test_local_different_path_is_replaced(tmp_path: Path):
    root = _write_catalog(tmp_path)
    other = tmp_path / "other-clone"
    other.mkdir()
    fake = FakeClaude(
        marketplaces=[{"name": "ai-plugins", "source": "path", "path": str(other)}]
    )
    assert icl.main(repo_root=root, run=fake) == 0
    assert fake.command_heads()[1:3] == [
        ("marketplace", "remove", "ai-plugins"),
        ("marketplace", "add", str(root)),
    ]


def test_missing_marketplace_adds_only(tmp_path: Path):
    root = _write_catalog(tmp_path)
    fake = FakeClaude(marketplaces=[])
    assert icl.main(repo_root=root, run=fake) == 0
    heads = fake.command_heads()
    assert ("marketplace", "remove", "ai-plugins") not in heads
    assert ("marketplace", "add", str(root)) in heads


def test_installed_plugin_is_updated(tmp_path: Path):
    root = _write_catalog(tmp_path, plugins=["foo"])
    fake = FakeClaude(
        marketplaces=[{"name": "ai-plugins", "source": "directory", "path": str(root)}],
        plugins=[{"name": "foo", "marketplace": "ai-plugins"}],
    )
    assert icl.main(repo_root=root, run=fake) == 0
    assert ("plugin", "update", "foo@ai-plugins") in fake.command_heads()
    assert not any(h[:2] == ("plugin", "install") for h in fake.command_heads())


def test_missing_plugin_is_installed(tmp_path: Path):
    root = _write_catalog(tmp_path, plugins=["foo"])
    fake = FakeClaude(
        marketplaces=[{"name": "ai-plugins", "source": "directory", "path": str(root)}],
        plugins=[],
    )
    assert icl.main(repo_root=root, run=fake) == 0
    assert ("plugin", "install", "foo@ai-plugins") in fake.command_heads()


def test_catalog_names_come_from_marketplace_json(tmp_path: Path):
    root = _write_catalog(tmp_path, name="local-market", plugins=["alpha"])
    fake = FakeClaude()
    assert icl.main(repo_root=root, run=fake) == 0
    assert ("plugin", "install", "alpha@local-market") in fake.command_heads()
    assert not any("foo@" in h[-1] for h in fake.command_heads() if h[0] == "plugin")


def test_plugin_install_failure_continues_and_exits_1(tmp_path: Path, capsys):
    root = _write_catalog(tmp_path, plugins=["foo", "bar"])
    fake = FakeClaude(fail_specs=frozenset({"foo@ai-plugins"}))
    assert icl.main(repo_root=root, run=fake) == 1
    heads = fake.command_heads()
    assert ("plugin", "install", "foo@ai-plugins") in heads
    assert ("plugin", "install", "bar@ai-plugins") in heads
    assert "failed plugins: foo" in capsys.readouterr().err


def test_marketplace_kind_github_and_git_url(tmp_path: Path):
    assert icl.marketplace_kind({"name": "x", "source": "github"}, tmp_path) == "remote"
    assert (
        icl.marketplace_kind(
            {"name": "x", "source": "git", "url": "https://github.com/org/repo.git"},
            tmp_path,
        )
        == "remote"
    )
    assert icl.marketplace_kind(None, tmp_path) == "missing"


def test_parse_wrapped_and_keyed_payloads():
    wrapped = icl.parse_list_payload(
        json.dumps({"marketplaces": [{"name": "ai-plugins", "source": "github"}]}),
        "marketplaces",
    )
    assert wrapped[0]["name"] == "ai-plugins"

    keyed = icl.parse_list_payload(
        json.dumps({"foo@ai-plugins": {"version": "1.0.0"}}),
        "plugins",
        "installed",
    )
    assert icl.plugin_is_installed(keyed, "foo", "ai-plugins")


def test_nested_source_object_is_remote(tmp_path: Path):
    entry = icl._normalize_entry(
        {"name": "ai-plugins", "source": {"source": "github", "repo": "org/repo"}}
    )
    assert icl.marketplace_kind(entry, tmp_path) == "remote"


def test_load_catalog_missing_file(tmp_path: Path):
    with pytest.raises(SystemExit, match="missing marketplace catalog"):
        icl.load_catalog(tmp_path)


def test_run_claude_missing_binary(monkeypatch):
    monkeypatch.setattr(icl.shutil, "which", lambda _name: None)
    with pytest.raises(SystemExit, match="claude not found on PATH"):
        icl.run_claude(["plugin", "list", "--json"])
