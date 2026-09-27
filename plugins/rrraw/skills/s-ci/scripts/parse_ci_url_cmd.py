"""CLI: parse-ci-url — forge/owner/repo (+ ids) from a CI run/job URL."""

from __future__ import annotations

import argparse

import emit
from ci_url import parse_ci_url_or_raise
from errors import CiUrlError

COMMAND = "parse-ci-url"


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Parse GitHub/GitLab CI run/job URL into forge + owner/repo",
        description="Result keys: forge, host, owner, repo, run_id, job_id",
    )
    parser.add_argument("url", help="Actions run/job or GitLab pipeline/job URL")
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    try:
        parsed = parse_ci_url_or_raise(args.url)
    except CiUrlError as exc:
        return emit.fail(COMMAND, exc.code, str(exc))
    except Exception as exc:
        return emit.fail_exception(COMMAND, exc)
    return emit.succeed(
        COMMAND,
        {
            "forge": parsed.forge,
            "host": parsed.host,
            "owner": parsed.owner,
            "repo": parsed.repo,
            "run_id": parsed.run_id,
            "job_id": parsed.job_id,
        },
    )
