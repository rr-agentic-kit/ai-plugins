from __future__ import annotations

import argparse
import os
import sys
from typing import Any

import emit
from errors import GlabError
from glab import GlabClient, api_list_pages, default_glab
from mr_common import resolve_mr_iid as _resolve_mr_iid

COMMAND = "mr-skip-threads"


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Bulk-reply and resolve all unresolved MR discussion threads",
        description="Result keys: unresolved_count, ok_count, fail_count",
    )
    parser.add_argument("mr_iid", nargs="?", help="Merge request IID")
    parser.add_argument("message", nargs="?", help="Reply message")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions without mutating"
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(mr_iid=args.mr_iid, message=args.message, dry_run=args.dry_run)


def _resolve_message(message: str | None) -> str:
    if message:
        return message
    return os.environ.get("MR_SKIP_MESSAGE", "skipped")


def _resolve_discussion(
    glab: GlabClient,
    mr_iid: str,
    discussion: dict[str, Any],
    message: str,
    *,
    dry_run: bool,
) -> bool:
    disc_id = discussion["id"]
    if dry_run:
        return _log_dry_run_discussion(mr_iid, disc_id, message)

    return _apply_discussion_resolution(glab, mr_iid, disc_id, message)


def _log_dry_run_discussion(mr_iid: str, disc_id: str, message: str) -> bool:
    reply_path = (
        f"projects/:fullpath/merge_requests/{mr_iid}/discussions/{disc_id}/notes"
    )
    resolve_path = f"projects/:fullpath/merge_requests/{mr_iid}/discussions/{disc_id}"
    print(
        f"dry-run: glab api --method POST {reply_path!r} -f body={message!r}",
        file=sys.stderr,
    )
    print(
        f"dry-run: glab api --method PUT {resolve_path!r} -f resolved=true",
        file=sys.stderr,
    )
    return True


def _apply_discussion_resolution(
    glab: GlabClient,
    mr_iid: str,
    disc_id: str,
    message: str,
) -> bool:
    try:
        glab.api(
            f"projects/:fullpath/merge_requests/{mr_iid}/discussions/{disc_id}/notes",
            method="POST",
            fields={"body": message},
        )
        glab.api(
            f"projects/:fullpath/merge_requests/{mr_iid}/discussions/{disc_id}",
            method="PUT",
            fields={"resolved": "true"},
        )
        print(f"ok: discussion {disc_id}", file=sys.stderr)
        return True
    except GlabError as exc:
        print(f"error: failed for discussion {disc_id}: {exc}", file=sys.stderr)
        return False


def _unresolved_discussions(glab: GlabClient, mr_iid: str) -> list[dict[str, Any]]:
    discussions = api_list_pages(
        glab,
        f"projects/:fullpath/merge_requests/{mr_iid}/discussions",
    )
    return [discussion for discussion in discussions if not discussion.get("resolved")]


def _process_threads(
    glab: GlabClient,
    mr_iid: str,
    message: str,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    unresolved = _unresolved_discussions(glab, mr_iid)
    _log_thread_batch_header(mr_iid, len(unresolved), dry_run=dry_run)
    ok_count, fail_count = _resolve_unresolved_threads(
        glab,
        mr_iid,
        unresolved,
        message,
        dry_run=dry_run,
    )

    print(
        f"summary: {ok_count} thread(s) processed, {fail_count} failure(s)",
        file=sys.stderr,
    )
    return {
        "unresolved_count": len(unresolved),
        "ok_count": ok_count,
        "fail_count": fail_count,
    }


def _log_thread_batch_header(
    mr_iid: str, unresolved_count: int, *, dry_run: bool
) -> None:
    print(f"MR IID: {mr_iid}", file=sys.stderr)
    if dry_run:
        print("dry-run: no API mutations will be performed", file=sys.stderr)
    print(f"unresolved discussions (this page): {unresolved_count}", file=sys.stderr)


def _resolve_unresolved_threads(
    glab: GlabClient,
    mr_iid: str,
    unresolved: list[dict[str, Any]],
    message: str,
    *,
    dry_run: bool,
) -> tuple[int, int]:
    ok_count = 0
    fail_count = 0
    for discussion in unresolved:
        if _resolve_discussion(glab, mr_iid, discussion, message, dry_run=dry_run):
            ok_count += 1
        else:
            fail_count += 1
    return ok_count, fail_count


def main(
    *,
    mr_iid: str | None = None,
    message: str | None = None,
    dry_run: bool = False,
    glab: GlabClient | None = None,
) -> int:
    def _run() -> int:
        client = glab or default_glab()
        resolved_iid = _resolve_mr_iid(client, mr_iid)
        resolved_message = _resolve_message(message)
        result = _process_threads(
            client, resolved_iid, resolved_message, dry_run=dry_run
        )
        if result["fail_count"] > 0:
            return emit.fail(
                COMMAND,
                "partial_failure",
                f"{result['fail_count']} thread(s) failed",
                result=result,
            )
        return emit.succeed(COMMAND, result)

    return emit.run_guarded(COMMAND, _run)
