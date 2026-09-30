"""argparse CLI for auto_learn --hook / --score (manual)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def require_python() -> None:
    if sys.version_info < (3, 14):  # noqa: UP036
        print(
            "auto_learn: need CPython 3.14+",
            file=sys.stderr,
        )
        raise SystemExit(127)


def run_hook_mode(runtime: str) -> int:
    from .hook import run_hook

    try:
        stdin_text = sys.stdin.read()
    except OSError:
        return 0
    try:
        out = run_hook(runtime=runtime, stdin_text=stdin_text)
    except Exception:
        return 0
    if out:
        sys.stdout.write(out)
        if not out.endswith("\n"):
            sys.stdout.write("\n")
    return 0


def run_score_mode(workspace: Path, session_id: str) -> int:
    """Debug: print score result for a session scratch dir (no inject)."""
    from .gates import default_workspace_roots, is_local_source_skill
    from .score import meets_inject_bar, score_events
    from .store import load_events, load_state, session_dir

    session = session_dir(workspace, session_id)
    if not session.is_dir():
        print(json.dumps({"ok": False, "reason": "no_session"}))
        return 1
    state = load_state(session)
    events = load_events(session)
    roots = default_workspace_roots([str(workspace)])
    bound = state.get("bound_skill")
    local = bool(bound and is_local_source_skill(str(bound), roots))
    hits = score_events(
        events,
        skill_bound=local,
        last_user_text=state.get("last_user_text"),
    )
    payload = {
        "ok": True,
        "bound_skill": bound,
        "local": local,
        "consumed": bool(state.get("consumed")),
        "signals": [
            {"id": h.class_id, "evidence": h.evidence, "extreme": h.extreme}
            for h in hits
        ],
        "meets_bar": meets_inject_bar(hits) and local and not state.get("consumed"),
    }
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auto_learn",
        description="Drift detector for recipe-context-engineer --auto-learn",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--hook",
        action="store_true",
        help="Dual-runtime hook adapter (stdin = host JSON)",
    )
    group.add_argument(
        "--score",
        action="store_true",
        help="Print score for an existing session scratch (debug)",
    )
    parser.add_argument(
        "--runtime",
        choices=("cursor", "claude"),
        help="Required with --hook: emit cursor or claude inject shape",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Workspace root for --score (default: cwd)",
    )
    parser.add_argument(
        "--session-id",
        default="default",
        help="Session id for --score",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    require_python()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.hook:
        if args.runtime is None:
            parser.error("--hook requires --runtime cursor|claude")
        return run_hook_mode(args.runtime)
    workspace = (args.workspace or Path.cwd()).resolve()
    return run_score_mode(workspace, args.session_id)
