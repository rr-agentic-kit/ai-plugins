"""Emit valid GitLab `new_line` anchors from MR unified diffs (`+` lines only)."""

from __future__ import annotations

import argparse
import re
from typing import Any

import emit
from glab import GlabClient, default_glab
from mr_common import auth_check as _auth_check
from mr_common import resolve_open_mr as _resolve_open_mr

COMMAND = "mr-inline-anchors"

_HUNK_RE = re.compile(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s+@@")


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Parse MR diffs for valid + new_line anchors per path",
        description=(
            "Resolve open MR, load diff_refs, fetch changes/diffs, parse unified "
            "diffs for + new-file line numbers. Result keys: mr_iid, diff_refs "
            "(base_sha/start_sha/head_sha), files (path → sorted + line ints). "
            "Optional --path filters."
        ),
    )
    parser.add_argument(
        "mr_ref",
        nargs="?",
        help="Optional MR URL, !IID, or numeric IID (omit to auto-discover open MR)",
    )
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        metavar="PATH",
        help="Limit to this path (repeatable); default: all changed files",
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(mr_ref=args.mr_ref, paths=args.paths)


def parse_unified_diff_plus_lines(diff_text: str) -> list[int]:
    """Return sorted unique new-file line numbers for addition (`+`) lines."""
    lines: set[int] = set()
    new_line = 0
    in_hunk = False
    for raw in (diff_text or "").splitlines():
        hunk = _HUNK_RE.match(raw)
        if hunk:
            new_line = int(hunk.group(1))
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if raw.startswith("\\"):
            continue
        if raw.startswith("+++") or raw.startswith("---"):
            continue
        if raw.startswith("+"):
            lines.add(new_line)
            new_line += 1
        elif raw.startswith("-"):
            continue
        else:
            # context line (leading space) or empty context
            new_line += 1
    return sorted(lines)


def _normalize_diff_refs(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, str] = {}
    for key in ("base_sha", "start_sha", "head_sha"):
        value = raw.get(key)
        if value:
            out[key] = str(value)
    return out


def _files_from_changes(
    changes: list[Any],
    *,
    path_filter: frozenset[str] | None,
) -> dict[str, list[int]]:
    files: dict[str, list[int]] = {}
    for change in changes:
        if not isinstance(change, dict):
            continue
        path = str(change.get("new_path") or change.get("old_path") or "")
        if not path:
            continue
        if path_filter is not None and path not in path_filter:
            continue
        plus_lines = parse_unified_diff_plus_lines(str(change.get("diff") or ""))
        if plus_lines:
            files[path] = plus_lines
        elif path_filter is not None or not change.get("deleted_file"):
            files.setdefault(path, [])
    return files


def _collect_anchors(
    glab: GlabClient,
    mr_ref: str | None,
    paths: list[str] | None,
) -> dict[str, Any]:
    _auth_check(glab)
    mr = _resolve_open_mr(glab, mr_ref)
    iid = str(mr.get("iid", ""))
    diff_refs = _normalize_diff_refs(mr.get("diff_refs"))

    payload = glab.api(f"projects/:fullpath/merge_requests/{iid}/changes")
    changes: list[Any] = []
    if isinstance(payload, dict):
        if not diff_refs:
            diff_refs = _normalize_diff_refs(payload.get("diff_refs"))
        raw_changes = payload.get("changes")
        if isinstance(raw_changes, list):
            changes = raw_changes
    elif isinstance(payload, list):
        changes = payload

    path_filter = frozenset(paths) if paths else None
    files = _files_from_changes(changes, path_filter=path_filter)
    return {
        "mr_iid": iid,
        "diff_refs": diff_refs,
        "files": files,
    }


def main(
    *,
    mr_ref: str | None = None,
    paths: list[str] | None = None,
    glab: GlabClient | None = None,
) -> int:
    def _run() -> int:
        client = glab or default_glab()
        result = _collect_anchors(client, mr_ref, paths)
        return emit.succeed(COMMAND, result)

    return emit.run_guarded(COMMAND, _run)
