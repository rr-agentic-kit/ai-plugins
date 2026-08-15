#!/usr/bin/env python3
"""Point Claude Code at this checkout and install or update catalog plugins."""

from __future__ import annotations

import json
import shutil
import subprocess  # nosec B404
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[1]
SCOPE = "user"
REMOTE_SOURCES = frozenset({"github", "git", "url"})

Runner = Callable[[list[str]], str]
MarketplaceKind = Literal["missing", "local", "remote"]


class ClaudeCommandError(Exception):
    def __init__(self, args: list[str], returncode: int, stderr: str) -> None:
        self.args = args
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(
            f"claude {' '.join(args)} failed (exit {returncode}): {stderr.strip()}"
        )


def run_claude(args: list[str]) -> str:
    claude = shutil.which("claude")
    if claude is None:
        raise SystemExit("claude not found on PATH")
    result = subprocess.run(  # nosec B603
        [claude, *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ClaudeCommandError(
            args, result.returncode, result.stderr or result.stdout
        )
    return result.stdout


def load_catalog(repo_root: Path) -> tuple[str, list[str]]:
    path = repo_root / ".claude-plugin" / "marketplace.json"
    if not path.is_file():
        raise SystemExit(f"missing marketplace catalog: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise SystemExit(f"missing marketplace name in {path}")
    plugins_raw = data.get("plugins")
    if not isinstance(plugins_raw, list) or not plugins_raw:
        raise SystemExit(f"no plugins listed in {path}")
    names: list[str] = []
    for entry in plugins_raw:
        if not isinstance(entry, dict):
            raise SystemExit(f"invalid plugin entry in {path}")
        plugin_name = entry.get("name")
        if not isinstance(plugin_name, str) or not plugin_name.strip():
            raise SystemExit(f"plugin missing name in {path}")
        names.append(plugin_name)
    return name, names


def parse_list_payload(raw: str, *container_keys: str) -> list[dict[str, Any]]:
    text = raw.strip()
    if not text:
        return []
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError:
        data = _extract_json(text)
    return _entries_from(data, container_keys)


def _extract_json(text: str) -> Any:
    starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
    if not starts:
        raise json.JSONDecodeError("no JSON in claude output", text, 0)
    start = min(starts)
    return json.loads(text[start:])


def _entries_from(data: Any, container_keys: tuple[str, ...]) -> list[dict[str, Any]]:
    if isinstance(data, list):
        entries: list[dict[str, Any]] = []
        for item in data:
            if isinstance(item, dict):
                entries.append(_normalize_entry(item))
            elif isinstance(item, str) and item.strip():
                entries.append(_normalize_entry({"name": item}))
        return entries
    if not isinstance(data, dict):
        return []
    for key in container_keys:
        if key in data:
            return _entries_from(data[key], ())
    entries = []
    for key, value in data.items():
        if not isinstance(key, str) or key.startswith("$"):
            continue
        if isinstance(value, dict):
            entries.append(_normalize_entry({**value, "_key": key}))
        elif isinstance(value, list) and value:
            first = value[0]
            if isinstance(first, dict):
                entries.append(_normalize_entry({**first, "_key": key}))
            elif isinstance(first, str):
                entries.append(_normalize_entry({"name": first, "_key": key}))
        elif value is True or isinstance(value, str):
            entries.append(_normalize_entry({"name": key, "_key": key}))
    return entries


def _normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    src = entry.get("source")
    if not isinstance(src, dict):
        return entry
    flattened = {**entry, **{k: v for k, v in src.items() if k != "source"}}
    if "source" in src:
        flattened["source"] = src["source"]
    else:
        flattened.pop("source", None)
    return flattened


def _is_remote_url(url: object) -> bool:
    if not isinstance(url, str) or not url.strip():
        return False
    lowered = url.strip().lower()
    prefixes = ("http://", "https://", "git@", "ssh://", "git://")
    return lowered.startswith(prefixes) or "github.com" in lowered


def marketplace_kind(entry: dict[str, Any] | None, repo_root: Path) -> MarketplaceKind:
    if entry is None:
        return "missing"
    source = str(entry.get("source") or "").strip().lower()
    repo = entry.get("repo")
    url = entry.get("url")
    path = entry.get("path")

    if source in REMOTE_SOURCES or (isinstance(repo, str) and repo.strip()):
        return "remote"
    if _is_remote_url(url):
        return "remote"

    if (
        isinstance(path, str)
        and path.strip()
        and Path(path).expanduser().resolve() == repo_root.resolve()
    ):
        return "local"
    return "remote"


def find_named_entry(entries: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for entry in entries:
        if entry.get("name") == name:
            return entry
    return None


def plugin_is_installed(
    entries: list[dict[str, Any]], plugin_name: str, marketplace_name: str
) -> bool:
    target = f"{plugin_name}@{marketplace_name}"
    for entry in entries:
        key = str(entry.get("_key") or entry.get("id") or "")
        if key == target or key.split(":", 1)[0] == target:
            return True
        name = entry.get("name") or entry.get("plugin")
        marketplace = (
            entry.get("marketplace")
            or entry.get("marketplaceName")
            or entry.get("sourceMarketplace")
        )
        if name == target:
            return True
        if name == plugin_name and marketplace == marketplace_name:
            return True
    return False


def ensure_local_marketplace(
    *,
    name: str,
    repo_root: Path,
    run: Runner,
) -> MarketplaceKind:
    raw = run(["plugin", "marketplace", "list", "--json"])
    entries = parse_list_payload(raw, "marketplaces")
    existing = find_named_entry(entries, name)
    kind = marketplace_kind(existing, repo_root)
    root = str(repo_root)
    if kind == "local":
        print(f"marketplace {name}: already local at {root}, skip")
        return kind
    if kind == "remote":
        print(f"marketplace {name}: remote source, replacing with {root}")
        run(["plugin", "marketplace", "remove", name, "--scope", SCOPE])
        run(["plugin", "marketplace", "add", root, "--scope", SCOPE])
        return kind
    print(f"marketplace {name}: adding local {root}")
    run(["plugin", "marketplace", "add", root, "--scope", SCOPE])
    return kind


def sync_plugins(
    *,
    marketplace_name: str,
    plugin_names: list[str],
    run: Runner,
) -> list[str]:
    raw = run(["plugin", "list", "--json"])
    installed = parse_list_payload(raw, "plugins", "installed")
    failed: list[str] = []
    for plugin_name in plugin_names:
        spec = f"{plugin_name}@{marketplace_name}"
        try:
            if plugin_is_installed(installed, plugin_name, marketplace_name):
                print(f"plugin {spec}: update")
                run(["plugin", "update", spec, "--scope", SCOPE])
            else:
                print(f"plugin {spec}: install")
                run(["plugin", "install", spec, "--scope", SCOPE, "--yes"])
        except ClaudeCommandError as exc:
            print(f"plugin {spec}: {exc}", file=sys.stderr)
            failed.append(plugin_name)
    return failed


def main(repo_root: Path = REPO_ROOT, run: Runner = run_claude) -> int:
    try:
        name, plugins = load_catalog(repo_root)
    except json.JSONDecodeError as exc:
        print(f"install_claude_local: {exc}", file=sys.stderr)
        return 1

    try:
        ensure_local_marketplace(name=name, repo_root=repo_root, run=run)
        failed = sync_plugins(marketplace_name=name, plugin_names=plugins, run=run)
    except ClaudeCommandError as exc:
        print(f"install_claude_local: {exc}", file=sys.stderr)
        return 1

    if failed:
        print(
            "install_claude_local: failed plugins: " + ", ".join(failed),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
