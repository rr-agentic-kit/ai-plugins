from __future__ import annotations

import argparse

import emit
from forge import detect

COMMAND = "detect-remote"


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Detect GitHub vs GitLab from origin remote",
        description="Result keys: forge, host, owner, repo",
    )
    parser.set_defaults(handler=_handler)


def _handler(_args: argparse.Namespace) -> int:
    try:
        remote = detect()
    except Exception as exc:
        return emit.fail_exception(COMMAND, exc)
    return emit.succeed(
        COMMAND,
        {
            "forge": remote.forge,
            "host": remote.host,
            "owner": remote.owner,
            "repo": remote.repo,
        },
    )
