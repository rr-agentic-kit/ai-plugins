#!/usr/bin/env python3
"""Resolve version-field merge conflicts by taking the latest semver.

Field-scoped: only ``version`` lines inside conflict hunks. Never whole-file
ours/theirs. Leaves non-version conflicts intact.

Invoke from the target git repo (cwd = repo root), or pass ``--repo``.

  python3 resolve_version_conflicts.py --plan
  python3 resolve_version_conflicts.py --apply

Stdout: key=value status block. Exit 0 on success; 1 on error; 2 if apply
left remaining non-version conflicts (partial success still wrote versions).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

VERSION_JSON_RE = re.compile(r'^(\s*)"version"\s*:\s*"(?P<ver>[^"]+)"\s*,?\s*$')
VERSION_TOML_RE = re.compile(r"^(\s*)version\s*=\s*\"(?P<ver>[^\"]+)\"\s*$")
CONFLICT_START = re.compile(r"^<<<<<<< .*$")
CONFLICT_BASE = re.compile(r"^\|\|\|\|\|\|\| .*$")
CONFLICT_MID = re.compile(r"^=======\s*$")
CONFLICT_END = re.compile(r"^>>>>>>> .*$")

# Paths where version auto-resolve is allowed (suffix / basename match).
PATH_SUFFIXES = (
    "/.cursor-plugin/plugin.json",
    "/.claude-plugin/plugin.json",
    "/plugin.json",
)
PATH_BASENAMES = frozenset(
    {
        "pyproject.toml",
        "marketplace.json",
    }
)


def _emit(**kwargs: object) -> None:
    for key, value in kwargs.items():
        if value is None:
            continue
        if isinstance(value, list):
            print(f"{key}={','.join(str(v) for v in value)}")
        else:
            print(f"{key}={value}")


def _fail(error: str, message: str, remediation: str = "") -> int:
    _emit(status="error", error=error, message=message, remediation=remediation or None)
    print(f"error: {message}", file=sys.stderr)
    if remediation:
        print(remediation, file=sys.stderr)
    return 1


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _parse_version(raw: str) -> tuple[tuple[int, ...], int, int]:
    """Sort key: (release_tuple, is_final, rc_num). Final > rc of same base."""
    text = raw.strip().strip("\"'")
    match = re.match(
        r"^(\d+(?:\.\d+)*)(?:-rc-(\d+))?$",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        # Unknown shape sorts below parseable versions but stays deterministic.
        return ((0,), 0, 0)
    base = tuple(int(part) for part in match.group(1).split("."))
    if match.group(2) is not None:
        return (base, 0, int(match.group(2)))
    return (base, 1, 0)


def latest_version(a: str, b: str) -> str:
    return a if _parse_version(a) >= _parse_version(b) else b


def _path_allowed(rel: str) -> bool:
    normalized = rel.replace("\\", "/")
    if Path(normalized).name in PATH_BASENAMES:
        return True
    return any(normalized.endswith(suffix) for suffix in PATH_SUFFIXES)


def _version_line_match(line: str) -> re.Match[str] | None:
    return VERSION_JSON_RE.match(line) or VERSION_TOML_RE.match(line)


def _rewrite_version_line(line: str, new_ver: str) -> str:
    json_match = VERSION_JSON_RE.match(line)
    if json_match:
        indent = json_match.group(1)
        trailing_comma = "," if line.rstrip().endswith(",") else ""
        return f'{indent}"version": "{new_ver}"{trailing_comma}\n'
    toml_match = VERSION_TOML_RE.match(line)
    if toml_match:
        indent = toml_match.group(1)
        return f'{indent}version = "{new_ver}"\n'
    raise ValueError(f"not a version line: {line!r}")


def _split_hunk_sides(
    hunk_lines: list[str],
) -> tuple[list[str], list[str], str, str]:
    """Return (ours, theirs, start_label_line, end_label_line)."""
    start = hunk_lines[0]
    end = hunk_lines[-1]
    body = hunk_lines[1:-1]
    mid_idx = None
    base_idx = None
    for i, line in enumerate(body):
        if CONFLICT_BASE.match(line):
            base_idx = i
        elif CONFLICT_MID.match(line):
            mid_idx = i
            break
    if mid_idx is None:
        raise ValueError("conflict hunk missing =======")
    ours = body[: base_idx if base_idx is not None and base_idx < mid_idx else mid_idx]
    # Drop base section when present (diff3).
    if base_idx is not None and base_idx < mid_idx:
        ours = body[:base_idx]
    theirs = body[mid_idx + 1 :]
    return ours, theirs, start, end


def _resolve_hunk(hunk_lines: list[str]) -> tuple[list[str], bool, bool]:
    """Resolve version lines in one conflict hunk.

    Returns (output_lines, version_resolved, still_conflicted).
    """
    ours, theirs, start, end = _split_hunk_sides(hunk_lines)
    ours_ver_idxs = [i for i, line in enumerate(ours) if _version_line_match(line)]
    theirs_ver_idxs = [i for i, line in enumerate(theirs) if _version_line_match(line)]

    if not ours_ver_idxs and not theirs_ver_idxs:
        return hunk_lines, False, True

    ours_ver = (
        _version_line_match(ours[ours_ver_idxs[0]]).group("ver")  # type: ignore[union-attr]
        if ours_ver_idxs
        else None
    )
    theirs_ver = (
        _version_line_match(theirs[theirs_ver_idxs[0]]).group("ver")  # type: ignore[union-attr]
        if theirs_ver_idxs
        else None
    )
    if ours_ver and theirs_ver:
        winner = latest_version(ours_ver, theirs_ver)
    else:
        winner = ours_ver or theirs_ver
    assert winner is not None

    # Template line for rewritten version (prefer ours formatting).
    template = ours[ours_ver_idxs[0]] if ours_ver_idxs else theirs[theirs_ver_idxs[0]]
    version_out = _rewrite_version_line(template, winner)

    ours_rest = [line for i, line in enumerate(ours) if i not in set(ours_ver_idxs)]
    theirs_rest = [
        line for i, line in enumerate(theirs) if i not in set(theirs_ver_idxs)
    ]

    if ours_rest == theirs_rest:
        # Version was the only dispute (or remaining sides identical).
        return [version_out, *ours_rest], True, False

    # Keep non-version disputes as a conflict; version already decided above.
    out = [version_out, start, *ours_rest, "=======\n", *theirs_rest, end]
    return out, True, True


def resolve_text(text: str) -> tuple[str, int, bool]:
    """Resolve version fields in conflicted text.

    Returns (new_text, versions_resolved_count, has_remaining_conflicts).
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    resolved = 0
    remaining = False
    while i < len(lines):
        if not CONFLICT_START.match(lines[i]):
            out.append(lines[i])
            i += 1
            continue
        j = i + 1
        while j < len(lines) and not CONFLICT_END.match(lines[j]):
            j += 1
        if j >= len(lines):
            out.extend(lines[i:])
            remaining = True
            break
        hunk = lines[i : j + 1]
        rewritten, did_version, still = _resolve_hunk(hunk)
        out.extend(rewritten)
        if did_version:
            resolved += 1
        if still:
            remaining = True
        i = j + 1
    # Detect any leftover markers.
    joined = "".join(out)
    if "<<<<<<< " in joined or ">>>>>>> " in joined:
        remaining = True
    return joined, resolved, remaining


def _unmerged_files(repo: Path) -> list[str]:
    proc = _run_git(repo, "diff", "--name-only", "--diff-filter=U")
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Auto-resolve version-field merge conflicts (latest semver)."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--plan",
        action="store_true",
        help="Print planned version resolutions; do not write",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Write version resolutions into the work tree",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Git repo root (default: cwd)",
    )
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        help="Limit to path(s); repeatable. Default: all unmerged allowed paths",
    )
    args = parser.parse_args(argv)

    repo = (args.repo or Path.cwd()).resolve()
    check = _run_git(repo, "rev-parse", "--show-toplevel")
    if check.returncode != 0:
        return _fail(
            "NOT_A_REPO",
            f"not a git repository: {repo}",
            "Run from REPO_ROOT or pass --repo",
        )
    repo = Path(check.stdout.strip())

    candidates = args.file or _unmerged_files(repo)
    if not candidates:
        _emit(status="ok", resolved=0, remaining=0, message="no unmerged files")
        return 0

    planned: list[str] = []
    applied: list[str] = []
    skipped: list[str] = []
    remaining_files: list[str] = []
    total_resolved = 0

    for rel in candidates:
        if not _path_allowed(rel):
            skipped.append(rel)
            continue
        path = repo / rel
        if not path.is_file():
            skipped.append(rel)
            continue
        original = path.read_text(encoding="utf-8")
        if "<<<<<<< " not in original:
            skipped.append(rel)
            continue
        new_text, count, still = resolve_text(original)
        if count == 0:
            skipped.append(rel)
            if still:
                remaining_files.append(rel)
            continue
        planned.append(f"{rel}:{count}")
        total_resolved += count
        if still:
            remaining_files.append(rel)
        if args.apply and new_text != original:
            path.write_text(new_text, encoding="utf-8")
            applied.append(rel)

    if args.plan:
        _emit(
            status="ok",
            mode="plan",
            resolved=total_resolved,
            remaining=len(remaining_files),
            files_planned=planned,
            files_remaining=remaining_files,
            files_skipped=skipped,
        )
        return 0

    _emit(
        status="ok" if not remaining_files else "partial",
        mode="apply",
        resolved=total_resolved,
        remaining=len(remaining_files),
        files_applied=applied,
        files_remaining=remaining_files,
        files_skipped=skipped,
    )
    # Exit 2 = versions fixed but other conflicts remain (agent must continue).
    if remaining_files and total_resolved > 0:
        return 2
    if remaining_files and total_resolved == 0:
        return 0
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(_fail("EXCEPTION", str(exc))) from exc
