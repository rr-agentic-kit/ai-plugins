from __future__ import annotations

import argparse
import sys

import emit
from errors import GlabError
from glab import GLAB_LIST_PAGE_SIZE, GLAB_SINGLE_PAGE, GlabClient, default_glab
from mr_common import auth_check as _auth_check
from mr_common import resolve_mr_iid as _resolve_mr_iid

COMMAND = "mr-ensure-review-instructions"
MARKER = "<!-- rr-ci:review-instructions -->"

NOTE_BODY = f"""{MARKER}
### Review comments on this MR

Inline comments were posted by an automated review.

Please address or reply on each thread. Re-request review when done.
"""


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Idempotently post review-fix instructions MR note",
        description="Result keys: action (already-present|posted|would-post)",
    )
    parser.add_argument("mr_iid", nargs="?", help="Merge request IID")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print note without posting"
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(mr_iid=args.mr_iid, dry_run=args.dry_run)


def _already_present(glab: GlabClient, mr_iid: str, user_id: int) -> bool:
    base_path = f"projects/:fullpath/merge_requests/{mr_iid}/notes"
    page = GLAB_SINGLE_PAGE
    while True:
        notes = glab.api(
            f"{base_path}?per_page={GLAB_LIST_PAGE_SIZE}&page={page}"
        )
        if not isinstance(notes, list):
            raise GlabError("unexpected notes API response (expected JSON array)")
        for note in notes:
            author = note.get("author") or {}
            body = note.get("body") or ""
            if author.get("id") == user_id and MARKER in body:
                return True
        if len(notes) < GLAB_LIST_PAGE_SIZE:
            break
        page += 1
    return False


def _emit_dry_run(_resolved_iid: str, _user_id: int) -> int:
    print(f"dry-run: would post general MR note with marker {MARKER}", file=sys.stderr)
    print("---", file=sys.stderr)
    print(NOTE_BODY, file=sys.stderr)
    print("---", file=sys.stderr)
    print("would-post", file=sys.stderr)
    return emit.succeed(
        COMMAND,
        {"action": "would-post"},
    )


def _post_review_note(glab: GlabClient, resolved_iid: str, _user_id: int) -> int:
    glab.api(
        f"projects/:fullpath/merge_requests/{resolved_iid}/notes",
        method="POST",
        input_json={"body": NOTE_BODY},
    )
    print("posted", file=sys.stderr)
    return emit.succeed(
        COMMAND,
        {"action": "posted"},
    )


def _ensure_note_posted(
    glab: GlabClient,
    resolved_iid: str,
    user_id: int,
    *,
    dry_run: bool,
) -> int:
    if _already_present(glab, resolved_iid, user_id):
        print("already-present", file=sys.stderr)
        return emit.succeed(
            COMMAND,
            {"action": "already-present"},
        )

    if dry_run:
        return _emit_dry_run(resolved_iid, user_id)

    return _post_review_note(glab, resolved_iid, user_id)


def _run_ensure_flow(
    client: GlabClient,
    resolved_iid: str,
    user_id: int,
    *,
    dry_run: bool,
) -> int:
    print(f"MR IID: {resolved_iid}", file=sys.stderr)
    print(f"user id: {user_id}", file=sys.stderr)
    if dry_run:
        print("dry-run: no API mutations will be performed", file=sys.stderr)

    return _ensure_note_posted(
        client,
        resolved_iid,
        user_id,
        dry_run=dry_run,
    )


def main(
    *,
    mr_iid: str | None = None,
    dry_run: bool = False,
    glab: GlabClient | None = None,
) -> int:
    def _run() -> int:
        client = glab or default_glab()
        _auth_check(client)
        resolved_iid = _resolve_mr_iid(client, mr_iid)
        me = client.api("user")
        user_id = me.get("id")
        if user_id is None:
            raise GlabError("could not resolve current GitLab user (glab api user)")

        return _run_ensure_flow(
            client,
            resolved_iid,
            user_id,
            dry_run=dry_run,
        )

    return emit.run_guarded(COMMAND, _run)
