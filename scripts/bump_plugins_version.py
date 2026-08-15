#!/usr/bin/env python3
"""Normalize all plugin/pyproject versions to PEP 440 max, then lockstep bump."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from packaging.version import InvalidVersion, Version

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from validate_plugin_versions import (  # noqa: E402
    REPO_ROOT,
    _read_pyproject_version,
    collect_versions,
    manifest_paths,
)

KINDS = ("major", "minor", "patch", "rc", "stable")
_PRE_LABEL = {"a": "alpha", "b": "beta", "c": "rc", "rc": "rc"}
_PYPROJECT_VERSION = re.compile(r'^version\s*=\s*"[^"]*"', re.MULTILINE)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Lift every plugin manifest and pyproject.toml to the PEP 440 max "
            "version, then increment. rc ticks local prerelease for plugin "
            "managers; other kinds use uv --bump --frozen."
        ),
    )
    parser.add_argument(
        "kind",
        choices=KINDS,
        help=(
            "Increment kind. rc ticks the local prerelease "
            "(0.0.2-beta-4 → 0.0.2-beta-5) so plugin managers refresh. "
            "stable graduates a prerelease (0.0.2-beta-4 → 0.0.2)."
        ),
    )
    return parser.parse_args(argv)


def pep440_max(versions: dict[str, str]) -> Version:
    parsed: list[Version] = []
    for label, raw in versions.items():
        try:
            parsed.append(Version(raw))
        except InvalidVersion as exc:
            raise SystemExit(f"invalid PEP 440 version in {label}: {raw}") from exc
    return max(parsed)


def increment_local(version: Version) -> str:
    """Tick prerelease so Claude/Cursor cache a new version string."""
    if version.pre is None:
        raise SystemExit(
            "rc increments a local prerelease so plugin managers pick up the "
            f"update; {version} is stable — use patch, minor, or major"
        )
    letter, num = version.pre
    if not isinstance(num, int):
        raise SystemExit(f"cannot increment prerelease {version.pre}")
    name = _PRE_LABEL.get(str(letter), str(letter))
    return f"{version.base_version}-{name}-{num + 1}"


def write_pyproject_version(path: Path, version: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, n = _PYPROJECT_VERSION.subn(f'version = "{version}"', text, count=1)
    if n != 1:
        raise SystemExit(f"could not replace version in {path}")
    path.write_text(updated, encoding="utf-8")


def write_manifest_version(path: Path, version: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"manifest is not an object: {path}")
    data["version"] = version
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_uv(args: list[str], *, cwd: Path) -> None:
    cmd = ["uv", *args]
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise SystemExit("uv not found on PATH") from exc
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip()
        raise SystemExit(f"uv {' '.join(args)} failed: {err}")


def _rel(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def run_bump(kind: str, repo_root: Path) -> str:
    versions = collect_versions(repo_root)
    max_v = pep440_max(versions)
    behind = [(label, raw) for label, raw in versions.items() if Version(raw) < max_v]

    if kind == "rc":
        old = next(raw for raw in versions.values() if Version(raw) == max_v)
        new = increment_local(max_v)
        write_pyproject_version(repo_root / "pyproject.toml", new)
        if behind:
            print(f"normalize: lifted {len(behind)} source(s) to {new}")
            for label, raw in behind:
                print(f"  {label}: {raw} -> {new}")
        else:
            print(f"normalize: already at {old}")
    else:
        old = str(max_v)
        restyled = any(raw != old for raw in versions.values())
        run_uv(["version", old, "--frozen"], cwd=repo_root)
        for manifest in manifest_paths(repo_root):
            write_manifest_version(manifest, old)
        if behind:
            print(f"normalize: lifted {len(behind)} source(s) to {old}")
            for label, raw in behind:
                print(f"  {label}: {raw} -> {old}")
        elif restyled:
            print(f"normalize: canonicalized to {old}")
        else:
            print(f"normalize: already at {old}")
        run_uv(["version", "--bump", kind, "--frozen"], cwd=repo_root)
        new = _read_pyproject_version(repo_root / "pyproject.toml")

    written = ["pyproject.toml"]
    for manifest in manifest_paths(repo_root):
        write_manifest_version(manifest, new)
        written.append(_rel(repo_root, manifest))

    print(f"{old} => {new}")
    print("wrote:")
    for rel in written:
        print(f"  {rel}")
    return new


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run_bump(args.kind, REPO_ROOT)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"bump_plugins_version: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
