#!/usr/bin/env python3
"""Session-state checkpoint CLI — project and mutate without loading
the whole file into agent context.

Invoke (from plugin root, with PYTHONPATH=scripts or via session_state.sh):
  python3 scripts/session_state_cli.py view --path <phase>/session-state.json
  python3 scripts/session_state_cli.py get --path ... --keys checkpoint,metadata
  python3 scripts/session_state_cli.py append-decision --path ... --json '{...}'

Stdout: one JSON envelope per call. Agents MUST NOT Read the checkpoint file whole;
use this CLI (or an equivalent projection). Full dump requires --i-know (anti-pattern).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any


def _envelope(
    command: str, *, ok: bool, result: Any = None, error: dict | None = None
) -> int:
    json.dump(
        {"command": command, "ok": ok, "result": result, "error": error}, sys.stdout
    )
    sys.stdout.write("\n")
    sys.stdout.flush()
    return 0 if ok else 1


def _fail(command: str, code: str, message: str) -> int:
    return _envelope(command, ok=False, error={"code": code, "message": message})


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("session-state root must be an object")
    return data


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=".session-state.", suffix=".json", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise


def _tail(items: Any, n: int) -> list[Any]:
    if not isinstance(items, list):
        return []
    if n <= 0:
        return []
    return items[-n:]


def cmd_view(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        return _fail("view", "MISSING_CHECKPOINT", f"not found: {path}")
    data = _load(path)
    preset = args.preset
    decisions_n = args.decisions
    assumptions_n = args.assumptions

    if preset == "status":
        result = {
            "metadata": data.get("metadata"),
            "checkpoint": data.get("checkpoint"),
            "preferences": data.get("preferences"),
        }
    elif preset == "tail":
        result = {
            "decisions_tail": _tail(data.get("decisions"), decisions_n),
            "assumptions_tail": _tail(data.get("assumptions"), assumptions_n),
            "level_facts_tail": {
                k: _tail(v, assumptions_n) if isinstance(v, list) else v
                for k, v in (data.get("level_facts") or {}).items()
            },
        }
    else:  # resume (default)
        result = {
            "metadata": data.get("metadata"),
            "checkpoint": data.get("checkpoint"),
            "preferences": data.get("preferences"),
            "resolution": data.get("resolution"),
            "cuts": data.get("cuts"),
            "project_posture": data.get("project_posture"),
            "discovery_complete": data.get("discovery_complete"),
            "frozen_levels": data.get("frozen_levels"),
            "decisions_tail": _tail(data.get("decisions"), decisions_n),
            "assumptions_tail": _tail(data.get("assumptions"), assumptions_n),
            "composed_docs": data.get("composed_docs"),
            "note_sessions": data.get("note_sessions"),
        }
        # Never include item_registry in presets (largest bloat).
    return _envelope(
        "view",
        ok=True,
        result={"path": str(path), "preset": preset, "projection": result},
    )


def cmd_get(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        return _fail("get", "MISSING_CHECKPOINT", f"not found: {path}")
    data = _load(path)
    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    if not keys:
        return _fail("get", "INVALID_ARGS", "provide --keys a,b,c")
    blocked = {"item_registry"} if not args.allow_registry else set()
    out: dict[str, Any] = {}
    for key in keys:
        if key in blocked:
            return _fail(
                "get",
                "READ_BUDGET",
                "item_registry blocked by default "
                "(use --allow-registry only when minting ids)",
            )
        if key not in data:
            return _fail("get", "KEY_MISSING", f"missing top-level key: {key}")
        out[key] = data[key]
    return _envelope(
        "get", ok=True, result={"path": str(path), "keys": keys, "projection": out}
    )


def cmd_dump(args: argparse.Namespace) -> int:
    if not args.i_know:
        return _fail(
            "dump",
            "READ_BUDGET",
            "full dump forbidden for agents; use view/get, "
            "or pass --i-know (anti-pattern)",
        )
    path = Path(args.path)
    if not path.is_file():
        return _fail("dump", "MISSING_CHECKPOINT", f"not found: {path}")
    data = _load(path)
    return _envelope(
        "dump",
        ok=True,
        result={"path": str(path), "data": data, "warning": "full dump"},
    )


def _parse_json_arg(raw: str, command: str) -> tuple[Any | None, int | None]:
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as e:
        return None, _fail(command, "INVALID_JSON", str(e))


def cmd_append_decision(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        return _fail("append-decision", "MISSING_CHECKPOINT", f"not found: {path}")
    obj, err = _parse_json_arg(args.json, "append-decision")
    if err is not None:
        return err
    if not isinstance(obj, dict):
        return _fail(
            "append-decision", "INVALID_JSON", "decision must be a JSON object"
        )
    data = _load(path)
    decisions = data.setdefault("decisions", [])
    if not isinstance(decisions, list):
        return _fail("append-decision", "SHAPE", "decisions is not a list")
    decisions.append(obj)
    if args.updated:
        meta = data.setdefault("metadata", {})
        if isinstance(meta, dict):
            meta["updated"] = args.updated
    _atomic_write(path, data)
    return _envelope(
        "append-decision",
        ok=True,
        result={
            "path": str(path),
            "id": obj.get("id"),
            "decisions_len": len(decisions),
        },
    )


def cmd_append_assumption(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        return _fail("append-assumption", "MISSING_CHECKPOINT", f"not found: {path}")
    obj, err = _parse_json_arg(args.json, "append-assumption")
    if err is not None:
        return err
    if not isinstance(obj, dict):
        return _fail(
            "append-assumption", "INVALID_JSON", "assumption must be a JSON object"
        )
    data = _load(path)
    assumptions = data.setdefault("assumptions", [])
    if not isinstance(assumptions, list):
        return _fail("append-assumption", "SHAPE", "assumptions is not a list")
    # upsert by id when present
    aid = obj.get("id")
    if aid:
        for i, row in enumerate(assumptions):
            if isinstance(row, dict) and row.get("id") == aid:
                assumptions[i] = {**row, **obj}
                _atomic_write(path, data)
                return _envelope(
                    "append-assumption",
                    ok=True,
                    result={"path": str(path), "id": aid, "upserted": True},
                )
    assumptions.append(obj)
    _atomic_write(path, data)
    return _envelope(
        "append-assumption",
        ok=True,
        result={"path": str(path), "id": aid, "assumptions_len": len(assumptions)},
    )


def cmd_set_checkpoint(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        return _fail("set-checkpoint", "MISSING_CHECKPOINT", f"not found: {path}")
    patch, err = _parse_json_arg(args.json, "set-checkpoint")
    if err is not None:
        return err
    if not isinstance(patch, dict):
        return _fail(
            "set-checkpoint", "INVALID_JSON", "checkpoint patch must be an object"
        )
    data = _load(path)
    cp = data.setdefault("checkpoint", {})
    if not isinstance(cp, dict):
        return _fail("set-checkpoint", "SHAPE", "checkpoint is not an object")
    # shallow merge; lists replace when provided
    for k, v in patch.items():
        cp[k] = v
    if args.updated:
        meta = data.setdefault("metadata", {})
        if isinstance(meta, dict):
            meta["updated"] = args.updated
    if args.raw_history_path:
        meta = data.setdefault("metadata", {})
        if isinstance(meta, dict):
            meta["raw_history_path"] = args.raw_history_path
    _atomic_write(path, data)
    return _envelope(
        "set-checkpoint", ok=True, result={"path": str(path), "checkpoint": cp}
    )


def cmd_append_level_fact(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        return _fail("append-level-fact", "MISSING_CHECKPOINT", f"not found: {path}")
    data = _load(path)
    facts = data.setdefault("level_facts", {})
    if not isinstance(facts, dict):
        return _fail("append-level-fact", "SHAPE", "level_facts is not an object")
    bucket = facts.setdefault(args.level, [])
    if not isinstance(bucket, list):
        return _fail(
            "append-level-fact", "SHAPE", f"level_facts.{args.level} is not a list"
        )
    bucket.append(args.text)
    _atomic_write(path, data)
    return _envelope(
        "append-level-fact",
        ok=True,
        result={"path": str(path), "level": args.level, "len": len(bucket)},
    )


def cmd_append_completed(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        return _fail("append-completed", "MISSING_CHECKPOINT", f"not found: {path}")
    data = _load(path)
    cp = data.setdefault("checkpoint", {})
    if not isinstance(cp, dict):
        return _fail("append-completed", "SHAPE", "checkpoint is not an object")
    completed = cp.setdefault("levels_completed", [])
    if not isinstance(completed, list):
        return _fail("append-completed", "SHAPE", "levels_completed is not a list")
    if args.id not in completed:
        completed.append(args.id)
    _atomic_write(path, data)
    return _envelope(
        "append-completed",
        ok=True,
        result={
            "path": str(path),
            "id": args.id,
            "levels_completed_len": len(completed),
        },
    )


def cmd_set_resolution(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        return _fail("set-resolution", "MISSING_CHECKPOINT", f"not found: {path}")
    obj, err = _parse_json_arg(args.json, "set-resolution")
    if err is not None:
        return err
    if not isinstance(obj, dict):
        return _fail("set-resolution", "INVALID_JSON", "resolution must be an object")
    data = _load(path)
    data["resolution"] = obj
    _atomic_write(path, data)
    return _envelope(
        "set-resolution", ok=True, result={"path": str(path), "resolution": obj}
    )


def cmd_set_metadata(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        return _fail("set-metadata", "MISSING_CHECKPOINT", f"not found: {path}")
    data = _load(path)
    meta = data.setdefault("metadata", {})
    if not isinstance(meta, dict):
        return _fail("set-metadata", "SHAPE", "metadata is not an object")
    if args.updated:
        meta["updated"] = args.updated
    if args.raw_history_path:
        meta["raw_history_path"] = args.raw_history_path
    if args.json:
        patch, err = _parse_json_arg(args.json, "set-metadata")
        if err is not None:
            return err
        if not isinstance(patch, dict):
            return _fail(
                "set-metadata", "INVALID_JSON", "metadata patch must be an object"
            )
        meta.update(patch)
    _atomic_write(path, data)
    return _envelope(
        "set-metadata", ok=True, result={"path": str(path), "metadata": meta}
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="session_state_cli", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    def add_path(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--path", required=True, help="Path to session-state.json")

    v = sub.add_parser(
        "view", help="Project resume/status/tail preset (default resume)"
    )
    add_path(v)
    v.add_argument("--preset", choices=("resume", "status", "tail"), default="resume")
    v.add_argument("--decisions", type=int, default=3, help="Tail length for decisions")
    v.add_argument(
        "--assumptions", type=int, default=5, help="Tail length for assumptions"
    )
    v.set_defaults(func=cmd_view)

    g = sub.add_parser("get", help="Project named top-level keys")
    add_path(g)
    g.add_argument("--keys", required=True, help="Comma-separated top-level keys")
    g.add_argument("--allow-registry", action="store_true")
    g.set_defaults(func=cmd_get)

    d = sub.add_parser("dump", help="Full file (anti-pattern; requires --i-know)")
    add_path(d)
    d.add_argument("--i-know", action="store_true")
    d.set_defaults(func=cmd_dump)

    ad = sub.add_parser("append-decision", help="Append one decisions[] object")
    add_path(ad)
    ad.add_argument("--json", required=True)
    ad.add_argument("--updated", default=None)
    ad.set_defaults(func=cmd_append_decision)

    aa = sub.add_parser(
        "append-assumption", help="Append or upsert assumptions[] by id"
    )
    add_path(aa)
    aa.add_argument("--json", required=True)
    aa.set_defaults(func=cmd_append_assumption)

    sc = sub.add_parser("set-checkpoint", help="Shallow-merge into checkpoint")
    add_path(sc)
    sc.add_argument("--json", required=True)
    sc.add_argument("--updated", default=None)
    sc.add_argument("--raw-history-path", default=None)
    sc.set_defaults(func=cmd_set_checkpoint)

    alf = sub.add_parser(
        "append-level-fact", help="Append string to level_facts[level]"
    )
    add_path(alf)
    alf.add_argument("--level", required=True)
    alf.add_argument("--text", required=True)
    alf.set_defaults(func=cmd_append_level_fact)

    ac = sub.add_parser(
        "append-completed", help="Append id to checkpoint.levels_completed"
    )
    add_path(ac)
    ac.add_argument("--id", required=True)
    ac.set_defaults(func=cmd_append_completed)

    sr = sub.add_parser("set-resolution", help="Replace resolution object")
    add_path(sr)
    sr.add_argument("--json", required=True)
    sr.set_defaults(func=cmd_set_resolution)

    sm = sub.add_parser("set-metadata", help="Patch metadata fields")
    add_path(sm)
    sm.add_argument("--updated", default=None)
    sm.add_argument("--raw-history-path", default=None)
    sm.add_argument("--json", default=None)
    sm.set_defaults(func=cmd_set_metadata)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        func: Callable[[argparse.Namespace], int] = args.func
        return func(args)
    except Exception as e:
        return _fail(getattr(args, "command", "session_state"), "EXCEPTION", str(e))


if __name__ == "__main__":
    raise SystemExit(main())
