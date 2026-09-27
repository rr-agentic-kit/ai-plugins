#!/usr/bin/env python3
"""Deterministic Node types probe for TypeScript process/Buffer misses.

  python3 node_types_probe.py --cwd <pkg-root> [--file <ts-path>] [--tsconfig <path>]

Stdout: JSON envelope. Exit 0 always when probe completes; 2 = usage.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

_TYPES_RE = re.compile(r'"types"\s*:\s*\[([^\]]*)\]', re.DOTALL)
_INCLUDE_RE = re.compile(r'"include"\s*:\s*\[([^\]]*)\]', re.DOTALL)
_STR_RE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')


def _strip_json_noise(text: str) -> str:
    """Drop // and /* */ comments so naive JSON / regex reads remain usable."""
    no_block = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//.*?$", "", no_block, flags=re.MULTILINE)


def _string_list(inner: str) -> list[str]:
    return [m.group(1) for m in _STR_RE.finditer(inner)]


def _find_package_root(start: Path) -> Path | None:
    cur = start if start.is_dir() else start.parent
    for candidate in [cur, *cur.parents]:
        if (candidate / "package.json").is_file():
            return candidate
    return None


def _load_package(pkg_root: Path) -> dict[str, Any]:
    return json.loads((pkg_root / "package.json").read_text(encoding="utf-8"))


def _has_types_node(pkg: dict[str, Any]) -> bool:
    for key in ("dependencies", "devDependencies", "optionalDependencies"):
        deps = pkg.get(key) or {}
        if isinstance(deps, dict) and "@types/node" in deps:
            return True
    return False


def _resolve_tsconfig(pkg_root: Path, explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit if explicit.is_file() else None
    for name in ("tsconfig.json", "tsconfig.app.json", "tsconfig.node.json"):
        path = pkg_root / name
        if path.is_file():
            return path
    return None


def _types_includes_node(tsconfig_text: str) -> bool | None:
    """True if types lists node; False if types present without node; None if types omitted."""
    cleaned = _strip_json_noise(tsconfig_text)
    match = _TYPES_RE.search(cleaned)
    if match is None:
        return None
    entries = [s.strip() for s in _string_list(match.group(1))]
    return "node" in entries


def _include_globs(tsconfig_text: str) -> list[str] | None:
    cleaned = _strip_json_noise(tsconfig_text)
    match = _INCLUDE_RE.search(cleaned)
    if match is None:
        return None
    return _string_list(match.group(1))


def _file_covered(pkg_root: Path, file_path: Path, include: list[str] | None) -> bool:
    if include is None:
        # No include key → tsc defaults to all files; treat as covered.
        return True
    try:
        rel = file_path.resolve().relative_to(pkg_root.resolve()).as_posix()
    except ValueError:
        return False
    for pattern in include:
        # tsconfig globs are relative to the config directory (≈ pkg_root here).
        normalized = pattern.replace("**/", "").replace("**", "*")
        if fnmatch(rel, pattern) or fnmatch(rel, normalized):
            return True
        # Also try basename-style **/foo
        if fnmatch(rel, f"**/{pattern.lstrip('./')}"):
            return True
    return False


def probe(
    cwd: Path,
    file_path: Path | None = None,
    tsconfig_path: Path | None = None,
) -> dict[str, Any]:
    pkg_root = _find_package_root(cwd if cwd.is_dir() else cwd.parent)
    if pkg_root is None:
        return {
            "verdict": "no_package_json",
            "next_action": "resolve_package_root",
            "has_types_node_dep": False,
            "types_includes_node": None,
            "file_in_include": None,
            "package_root": None,
            "tsconfig": None,
        }

    pkg = _load_package(pkg_root)
    has_dep = _has_types_node(pkg)
    tsconfig = _resolve_tsconfig(pkg_root, tsconfig_path)
    if tsconfig is None:
        return {
            "verdict": "no_tsconfig",
            "next_action": "resolve_tsconfig",
            "has_types_node_dep": has_dep,
            "types_includes_node": None,
            "file_in_include": None,
            "package_root": str(pkg_root),
            "tsconfig": None,
        }

    text = tsconfig.read_text(encoding="utf-8")
    types_node = _types_includes_node(text)
    include = _include_globs(text)
    file_in: bool | None = None
    if file_path is not None:
        file_in = _file_covered(pkg_root, file_path, include)

    if not has_dep:
        verdict, next_action = "missing_dep", "add_types_node_dep"
    elif types_node is False or types_node is None:
        # TS 6 empty default / omitted → treat as missing for Node globals path.
        verdict, next_action = "missing_types", "set_types_node"
    elif file_path is not None and file_in is False:
        verdict, next_action = (
            "file_outside_include",
            "extend_include_or_node_process_import",
        )
    else:
        verdict, next_action = "ready", "none"

    return {
        "verdict": verdict,
        "next_action": next_action,
        "has_types_node_dep": has_dep,
        "types_includes_node": types_node,
        "file_in_include": file_in,
        "package_root": str(pkg_root),
        "tsconfig": str(tsconfig),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Node types probe for TS process/Buffer misses"
    )
    parser.add_argument(
        "--cwd", type=Path, default=Path.cwd(), help="Package / app root to search"
    )
    parser.add_argument("--file", type=Path, default=None, help="Failing .ts/.tsx path")
    parser.add_argument(
        "--tsconfig", type=Path, default=None, help="Explicit tsconfig path"
    )
    args = parser.parse_args(argv)

    if not args.cwd.exists():
        print(
            json.dumps(
                {
                    "command": "node-types-probe",
                    "ok": False,
                    "result": None,
                    "error": f"cwd does not exist: {args.cwd}",
                }
            )
        )
        return 2

    result = probe(args.cwd, args.file, args.tsconfig)
    print(
        json.dumps(
            {
                "command": "node-types-probe",
                "ok": True,
                "result": result,
                "error": None,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
