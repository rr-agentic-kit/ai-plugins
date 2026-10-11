#!/usr/bin/env python3
"""Build a GitHub Release zip of the dual-runtime marketplace install tree."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
import zipfile
from pathlib import Path

from packaging.version import InvalidVersion, Version

REPO_ROOT = Path(__file__).resolve().parents[1]

ROOT_DOC_FILES = ("LICENSE", "README.md", "INSTALL.md", "INSTALL-AI.md")
MARKETPLACE_ROOT_DIRS = (".cursor-plugin", ".claude-plugin")
_SKIP_DIR_NAMES = frozenset(
    {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git"}
)


def read_pyproject_version(pyproject: Path) -> str:
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    version = data.get("project", {}).get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"missing [project].version in {pyproject}")
    return version


def catalog_plugin_names(repo_root: Path) -> list[str]:
    marketplace = repo_root / ".cursor-plugin" / "marketplace.json"
    if not marketplace.is_file():
        raise FileNotFoundError(f"missing marketplace catalog: {marketplace}")
    data = json.loads(marketplace.read_text(encoding="utf-8"))
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise ValueError(f"no plugins in {marketplace}")
    names: list[str] = []
    for entry in plugins:
        if not isinstance(entry, dict):
            raise ValueError(f"invalid plugin entry in {marketplace}")
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"plugin entry missing name in {marketplace}")
        names.append(name)
    return names


def _should_skip_path(path: Path) -> bool:
    allowed_dot_dirs = {".cursor-plugin", ".claude-plugin"}
    for part in path.parts:
        if part in _SKIP_DIR_NAMES:
            return True
        if part.startswith(".") and part not in allowed_dot_dirs:
            return True
    return False


def release_staging_paths(repo_root: Path) -> list[Path]:
    """Repo-relative paths included in the marketplace release zip."""
    repo_root = repo_root.resolve()
    paths: list[Path] = []

    for name in ROOT_DOC_FILES:
        candidate = repo_root / name
        if candidate.is_file():
            paths.append(candidate.relative_to(repo_root))

    for sub in MARKETPLACE_ROOT_DIRS:
        root_mp = repo_root / sub
        if not root_mp.is_dir():
            continue
        for file_path in root_mp.rglob("*"):
            if file_path.is_file() and not _should_skip_path(
                file_path.relative_to(repo_root)
            ):
                paths.append(file_path.relative_to(repo_root))

    plugins_dir = repo_root / "plugins"
    if plugins_dir.is_dir():
        for file_path in plugins_dir.rglob("*"):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(repo_root)
            if _should_skip_path(rel):
                continue
            paths.append(rel)

    catalog = catalog_plugin_names(repo_root)
    for name in catalog:
        plugin_dir = plugins_dir / name
        if not plugin_dir.is_dir():
            raise FileNotFoundError(f"catalog plugin missing directory: plugins/{name}")

    return sorted(set(paths))


def zip_archive_top_dir(version: str) -> str:
    return f"ai-plugins-{version}"


def zip_output_name(version: str) -> str:
    return f"ai-plugins-{version}.zip"


def is_prerelease_version(version: str) -> bool:
    try:
        return Version(version).is_prerelease
    except InvalidVersion as exc:
        raise ValueError(f"invalid version '{version}'") from exc


def build_marketplace_zip(
    repo_root: Path,
    output_dir: Path,
    *,
    version: str | None = None,
) -> Path:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    resolved_version = version or read_pyproject_version(repo_root / "pyproject.toml")
    staging = release_staging_paths(repo_root)
    if not staging:
        raise ValueError(f"no release paths under {repo_root}")

    archive_path = output_dir / zip_output_name(resolved_version)
    top = zip_archive_top_dir(resolved_version)

    with zipfile.ZipFile(
        archive_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zf:
        for rel in staging:
            source = repo_root / rel
            if not source.is_file():
                raise FileNotFoundError(f"release path missing: {rel}")
            zf.write(source, arcname=f"{top}/{rel.as_posix()}")

    return archive_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: parent of scripts/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "dist",
        help="Directory for the zip artifact (default: dist/)",
    )
    parser.add_argument(
        "--version",
        help="Override version string (default: read from pyproject.toml)",
    )
    parser.add_argument(
        "--print-prerelease",
        action="store_true",
        help="Print prerelease=true|false for CI and exit without building",
    )
    args = parser.parse_args(argv)

    try:
        version = args.version or read_pyproject_version(
            args.repo_root / "pyproject.toml"
        )
        if args.print_prerelease:
            flag = "true" if is_prerelease_version(version) else "false"
            print(f"prerelease={flag}")
            return 0
        archive = build_marketplace_zip(
            args.repo_root,
            args.output_dir,
            version=version,
        )
    except (OSError, ValueError, json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"build_marketplace_zip: {exc}", file=sys.stderr)
        return 1

    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
