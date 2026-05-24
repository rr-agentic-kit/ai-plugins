#!/usr/bin/env python3
"""Fail if plugin and repo version fields are not identical."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_pyproject_version(pyproject: Path) -> str:
    import tomllib

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


def collect_versions(repo_root: Path) -> dict[str, str]:
    pyproject = repo_root / "pyproject.toml"
    plugins_dir = repo_root / "plugins"
    versions: dict[str, str] = {}
    versions["pyproject.toml [project].version"] = _read_pyproject_version(pyproject)

    if not plugins_dir.is_dir():
        raise SystemExit(f"plugins directory not found: {plugins_dir}")

    plugin_dirs = sorted(
        p for p in plugins_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
    )
    if not plugin_dirs:
        raise SystemExit(f"no plugin directories under {plugins_dir}")

    for plugin_dir in plugin_dirs:
        name = plugin_dir.name
        for rel in (
            ".cursor-plugin/plugin.json",
            ".claude-plugin/plugin.json",
        ):
            manifest = plugin_dir / rel
            label = f"plugins/{name}/{rel}"
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
