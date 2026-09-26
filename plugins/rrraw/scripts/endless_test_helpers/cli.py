#!/usr/bin/env python3
"""Deterministic helpers for s-test-endless orchestration phases."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

COUNTS_RE = re.compile(
    r"COUNTS:\s*MISSING=(\d+)\s*\|\s*NON-COMPLIANT=(\d+)\s*\|\s*"
    r"OVER-TESTED=(\d+)\s*\|\s*UNCLEAR=(\d+)\s*\|\s*ADEQUATE=(\d+)"
)
STEP_LINE_RE = re.compile(r"^\- \[ \] \*\*Step")
TARGET_FILE_RE = re.compile(r"`([^`]+)`")


def _load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    data: dict[str, object] = {}
    for line in block.splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip().strip("'\"")
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = (
                [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
                if inner
                else []
            )
        elif val.isdigit():
            data[key] = int(val)
        else:
            data[key] = val
    return data


def _plan_paths(plans_dir: Path, chunk: str | None) -> list[Path]:
    paths = sorted(plans_dir.glob("trp-*.md"))
    if chunk is None:
        return paths
    return [
        p for p in paths if chunk in p.name or chunk in p.read_text(encoding="utf-8")
    ]


def _file_set(path: Path, fm: dict) -> set[str]:
    if fm.get("target_files"):
        return {str(x) for x in fm["target_files"]}
    body = path.read_text(encoding="utf-8")
    found = set(TARGET_FILE_RE.findall(body))
    return {f for f in found if "/" in f or "." in f}


def cmd_packing_probes(args: argparse.Namespace) -> int:
    plans_dir = Path(args.plans_dir)
    paths = _plan_paths(plans_dir, args.chunk)
    if not paths:
        print("ok: no plans", file=sys.stderr)
        return 0

    packs: list[tuple[Path, dict, set[str], int]] = []
    for p in paths:
        fm = _load_frontmatter(p)
        if "estimated_context_units" not in fm:
            print("skip: missing estimated_context_units", file=sys.stderr)
            return 0
        steps = len(STEP_LINE_RE.findall(p.read_text(encoding="utf-8")))
        packs.append((p, fm, _file_set(p, fm), steps))

    # micro_packs
    multi = [x for x in packs if len(packs) >= 2]
    if multi:
        one_step = sum(1 for _, _, _, s in packs if s == 1)
        if one_step >= max(1, len(packs) // 2):
            print("probe: micro_packs")
            print(
                "PACKING_RETRY: bin-pack toward HARD_MAX; mixed fill small "
                "steps into remaining headroom"
            )
            return 1

    # parallel_collision
    by_group: dict[str, list[tuple[Path, set[str]]]] = defaultdict(list)
    for p, fm, files, _ in packs:
        g = fm.get("parallel_group") or ""
        if g:
            by_group[g].append((p, files))
    for group, items in by_group.items():
        for i, (_, a) in enumerate(items):
            for j, (_, b) in enumerate(items):
                if i < j and a & b:
                    print(f"probe: parallel_collision group={group}")
                    return 2

    print("ok: all probes pass")
    return 0


def cmd_dispatch_queue(args: argparse.Namespace) -> int:
    plans_dir = Path(args.plans_dir)
    paths = _plan_paths(plans_dir, None)
    nodes: list[dict] = []
    for p in paths:
        fm = _load_frontmatter(p)
        nodes.append(
            {
                "plan_path": str(p),
                "pack_sequence": fm.get("pack_sequence", 0),
                "sequential_after": fm.get("sequential_after"),
                "parallel_group": fm.get("parallel_group", ""),
                "branch_name": fm.get("branch", ""),
                "files": sorted(_file_set(p, fm)),
            }
        )

    nodes.sort(key=lambda n: (n["pack_sequence"], n["plan_path"]))
    layers: list[list[dict]] = []
    done: set[str] = set()
    remaining = nodes[:]
    while remaining:
        ready = [
            n
            for n in remaining
            if not n["sequential_after"] or n["sequential_after"] in done
        ]
        if not ready:
            print("error: unknown sequential_after", file=sys.stderr)
            return 1
        batch: list[dict] = []
        used_files: set[str] = set()
        for n in sorted(ready, key=lambda x: x["pack_sequence"]):
            if set(n["files"]) & used_files:
                continue
            batch.append(n)
            used_files |= set(n["files"])
        if not batch:
            print(
                "packing_gate: intersecting file sets in ready layer", file=sys.stderr
            )
            return 1
        max_p = args.max_parallel
        if max_p and max_p > 0:
            batch = batch[:max_p]
        layers.append(batch)
        for n in batch:
            done.add(n["plan_path"])
            remaining.remove(n)

    print(json.dumps({"layers": layers}, indent=2))
    return 0


def _parse_counts(text: str) -> tuple[int, int, int, int, int] | None:
    m = COUNTS_RE.search(text)
    if not m:
        return None
    a, b, c, d, e = (int(x) for x in m.groups())
    return a, b, c, d, e


def cmd_aggregate_counts(args: argparse.Namespace) -> int:
    totals = [0, 0, 0, 0, 0]
    rows: list[str] = []
    for raw in args.assess:
        path = Path(raw)
        text = path.read_text(encoding="utf-8")
        parsed = _parse_counts(text)
        if parsed is None:
            print(f"parse error: {path}", file=sys.stderr)
            return 1
        for i, v in enumerate(parsed):
            totals[i] += v
        if "|" in text:
            for line in text.splitlines():
                if line.startswith("|") and "---" not in line and "Target" not in line:
                    rows.append(line)

    print(
        "COUNTS: "
        f"MISSING={totals[0]} | NON-COMPLIANT={totals[1]} | "
        f"OVER-TESTED={totals[2]} | UNCLEAR={totals[3]} | ADEQUATE={totals[4]}"
    )
    if rows:
        print("| Target | Verdict | Evidence |")
        print("| --- | --- | --- |")
        for row in rows:
            print(row)
    return 0


def _grouping_label(files: set[str]) -> str:
    if not files:
        return "(none)"
    prefixes = []
    for f in sorted(files):
        parts = Path(f).parts
        prefixes.append("/".join(parts[:2]) if len(parts) > 1 else parts[0])
    return min(prefixes)


def cmd_manifest_table(args: argparse.Namespace) -> int:
    plans_dir = Path(args.plans_dir)
    paths = _plan_paths(plans_dir, None)
    print(f"## Endless add-test — iteration {args.iteration} / Work-pack dispatch\n")
    print(
        "| pack_sequence | plan_path | branch_name | sequential_after | "
        "parallel_group | Grouping (heuristic) |"
    )
    print("| --- | --- | --- | --- | --- | --- |")
    for p in paths:
        fm = _load_frontmatter(p)
        files = _file_set(p, fm)
        print(
            f"| {fm.get('pack_sequence', '')} | {p} | {fm.get('branch', '')} | "
            f"{fm.get('sequential_after', '')} | {fm.get('parallel_group', '')} | "
            f"{_grouping_label(files)} |"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="s-test-endless orchestration helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_probe = sub.add_parser("packing-probes")
    p_probe.add_argument("--plans-dir", required=True)
    p_probe.add_argument("--chunk", default=None)

    p_queue = sub.add_parser("dispatch-queue")
    p_queue.add_argument("--plans-dir", required=True)
    p_queue.add_argument("--max-parallel", type=int, default=0)

    p_counts = sub.add_parser("aggregate-counts")
    p_counts.add_argument("--assess", action="append", required=True)

    p_manifest = sub.add_parser("manifest-table")
    p_manifest.add_argument("--plans-dir", required=True)
    p_manifest.add_argument("--iteration", required=True)

    args = parser.parse_args()
    handlers = {
        "packing-probes": cmd_packing_probes,
        "dispatch-queue": cmd_dispatch_queue,
        "aggregate-counts": cmd_aggregate_counts,
        "manifest-table": cmd_manifest_table,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
