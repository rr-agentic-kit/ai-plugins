from __future__ import annotations

import argparse
import sys
from typing import Any

import emit
from glab import GlabClient, default_glab
from mr_common import auth_check as _auth_check
from pending_reviews_graphql import REVIEW_QUEUE_QUERY

COMMAND = "pending-reviews"


def _unresolved_discussion_count(mr: dict[str, Any]) -> int:
    resolvable = mr.get("resolvableDiscussionsCount") or 0
    resolved = mr.get("resolvedDiscussionsCount") or 0
    return int(resolvable) - int(resolved)


def _ready_urls(nodes: list[dict[str, Any]]) -> list[str]:
    urls: list[str] = []
    for mr in nodes:
        if _unresolved_discussion_count(mr) > 0:
            continue
        web_url = mr.get("webUrl")
        if web_url:
            urls.append(str(web_url))
    return sorted(urls)


def _parse_review_queue(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    current_user = data.get("currentUser")
    if not isinstance(current_user, dict):
        return {}
    review_queue = current_user.get("reviewRequestedMergeRequests")
    if not isinstance(review_queue, dict):
        return {}
    return review_queue


def _fetch_review_queue(glab: GlabClient) -> list[dict[str, Any]]:
    all_nodes: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        data = glab.graphql(REVIEW_QUEUE_QUERY, variables={"after": after})
        review_queue = _parse_review_queue(data)
        nodes = review_queue.get("nodes") or []
        all_nodes.extend(nodes)
        page_info = review_queue.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            break
    return all_nodes


def _pending_reviews(glab: GlabClient) -> dict[str, Any]:
    _auth_check(glab)
    all_nodes = _fetch_review_queue(glab)
    urls = _ready_urls(all_nodes)
    print(
        f"fetched {len(all_nodes)} MRs, {len(urls)} ready",
        file=sys.stderr,
    )
    return {"count": len(urls), "urls": urls}


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="List open MRs awaiting the current user's review",
        description="Result keys: count, urls",
    )
    parser.set_defaults(handler=_handler)


def _handler(_args: argparse.Namespace) -> int:
    return main()


def main(glab: GlabClient | None = None) -> int:
    def _run() -> int:
        client = glab or default_glab()
        result = _pending_reviews(client)
        return emit.succeed(COMMAND, result)

    return emit.run_guarded(COMMAND, _run)
