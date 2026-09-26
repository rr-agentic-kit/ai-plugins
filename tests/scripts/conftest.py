"""Shared fixtures for repo script tests."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
import install_claude_local as icl  # noqa: E402
import validate_plugin_versions as m  # noqa: E402
from release_branches import GhError, GitError  # noqa: E402


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


class FakeGh:
    def __init__(self, repo: str | None = None) -> None:
        self._default_repo = repo
        self.calls: list[tuple[tuple[str, ...], str | None]] = []
        self.responses: dict[tuple[str, ...], str] = {}
        self.errors: set[tuple[str, ...]] = set()
        self.branches: list[str] = []
        self.default_branch = "master"
        self.prs: dict[str, dict[str, str]] = {}
        self.workflow_runs = "run-1\tqueued"

    def run(self, args: Sequence[str], *, repo: str | None = None) -> str:
        key = tuple(args)
        self.calls.append((key, repo if repo is not None else self._default_repo))
        if key in self.errors:
            raise GhError("simulated gh failure")

        if key in self.responses:
            return self.responses[key]

        if key[:3] == ("api", "repos/{owner}/{repo}/branches", "--paginate"):
            return "\n".join(self.branches)

        if key[:2] == ("api",) and "/branches/" in key[1]:
            branch_name = key[1].split("/branches/", 1)[1]
            if branch_name in self.branches and "--silent" in key:
                return ""
            raise GhError("branch not found")

        if key[:4] == ("repo", "view", "--json", "defaultBranchRef"):
            return self.default_branch

        if key[:2] == ("auth", "status"):
            return ""

        if key[:2] == ("pr", "list"):
            head = key[key.index("--head") + 1]
            matches = [pr for pr in self.prs.values() if pr["head"] == head]
            return json.dumps(matches)

        if key[:2] == ("pr", "edit"):
            number = key[2]
            self.prs[number]["title"] = key[key.index("--title") + 1]
            return ""

        if key[:2] == ("pr", "create"):
            url = "https://github.com/example/pr/99"
            head = key[key.index("--head") + 1]
            self.prs["99"] = {"url": url, "number": "99", "head": head}
            return url

        if key[:2] == ("run", "list"):
            return self.workflow_runs

        if key[:2] == ("run", "watch"):
            return ""

        if key[:2] == ("workflow", "run"):
            return ""

        return ""


class FakeGit:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.calls: list[tuple[tuple[str, ...], Path]] = []
        self.workflows: set[str] = set()
        self.local_branches: set[str] = set()
        self.remote_branches: set[str] = set()
        self.current_branch = "feat/test"

    def run(self, args: Sequence[str], *, cwd: Path) -> str:
        key = tuple(args)
        self.calls.append((key, cwd))

        if key[:2] == ("ls-remote", "--heads"):
            pattern = key[-1]
            prefix = pattern.removesuffix("*")
            matches = sorted(
                ref for ref in self.remote_branches if ref.startswith(prefix)
            )
            return "\n".join(f"deadbeef refs/heads/{ref}" for ref in matches)

        if key[:2] == ("ls-remote", "--exit-code"):
            head = key[-1]
            if head in self.remote_branches:
                return f"deadbeef refs/heads/{head}"
            raise GitError("not found")

        if key[:2] == ("show-ref", "--verify"):
            branch = key[-1].removeprefix("refs/heads/")
            if branch in self.local_branches:
                return ""
            raise GitError("not found")

        if key[:2] == ("rev-parse", "--abbrev-ref"):
            return self.current_branch

        if key[:2] == ("cat-file", "-e"):
            rev_path = key[2]
            if rev_path in self.workflows:
                return ""
            raise GitError("missing")

        if key[:2] == ("fetch", "origin"):
            return ""

        if key[0] == "branch":
            return ""

        if key[:3] == ("checkout", "--no-track", "-b"):
            return ""

        if key[:2] == ("push", "-u"):
            return ""

        return ""


@pytest.fixture
def fake_gh() -> FakeGh:
    return FakeGh()


@pytest.fixture
def fake_git(tmp_path: Path) -> FakeGit:
    return FakeGit(tmp_path / "repo")
