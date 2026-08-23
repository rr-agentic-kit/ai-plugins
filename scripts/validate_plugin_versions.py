#!/usr/bin/env python3
"""Fail if plugin and repo version fields are not identical."""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_MANIFEST_RELS = (
    ".cursor-plugin/plugin.json",
    ".claude-plugin/plugin.json",
)


def _read_pyproject_version(pyproject: Path) -> str:
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    version = data.get("project", {}).get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"missing [project].version in {pyproject}")
    return version


def _read_manifest_version(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"missing version in {path}")
    return version


def _plugin_dirs(repo_root: Path) -> list[Path]:
    plugins_dir = repo_root / "plugins"
    if not plugins_dir.is_dir():
        raise SystemExit(f"plugins directory not found: {plugins_dir}")

    dirs = sorted(
        p for p in plugins_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
    )
    if not dirs:
        raise SystemExit(f"no plugin directories under {plugins_dir}")
    return dirs


def manifest_paths(repo_root: Path) -> list[Path]:
    """Cursor and Claude plugin.json paths for every plugin directory."""
    return [
        plugin_dir / rel
        for plugin_dir in _plugin_dirs(repo_root)
        for rel in _MANIFEST_RELS
    ]


def collect_versions(repo_root: Path) -> dict[str, str]:
    pyproject = repo_root / "pyproject.toml"
    versions: dict[str, str] = {}
    versions["pyproject.toml [project].version"] = _read_pyproject_version(pyproject)

    for manifest in manifest_paths(repo_root):
        label = manifest.relative_to(repo_root).as_posix()
        if not manifest.is_file():
            raise SystemExit(f"missing manifest: {label}")
        versions[label] = _read_manifest_version(manifest)

    return versions


def main() -> int:
    try:
        versions = collect_versions(REPO_ROOT)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"validate_plugin_versions: {exc}", file=sys.stderr)
        return 1

    unique = sorted(set(versions.values()))
    if len(unique) == 1:
        print(f"version alignment ok: {unique[0]}")
        return 0

    print("version mismatch — all sources must use the same version:", file=sys.stderr)
    for label, value in versions.items():
        print(f"  {label}: {value}", file=sys.stderr)
    print(
        f"\nexpected one version, found: {', '.join(unique)}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
