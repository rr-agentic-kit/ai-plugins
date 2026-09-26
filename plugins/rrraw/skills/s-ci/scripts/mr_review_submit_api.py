from __future__ import annotations

from typing import Any, Literal

from errors import GlabError
from glab import GlabClient
from mr_review_submit_graphql import (
    REQUEST_CHANGES_MUTATION,
    REVIEWERS_QUERY,
    SET_REVIEWERS_MUTATION,
)

COMMAND = "mr-review-submit"
HTTP_FORBIDDEN_STATUS = "403"

Decision = Literal["request-changes", "approve", "none"]
Status = Literal[
    "requested_changes",
    "approved",
    "reviewer_only",
    "unchanged",
    "rejected",
    "would-submit",
]


def _mutation_errors(result: dict[str, Any] | None, field: str) -> list[str]:
    if not result:
        return ["empty graphql response"]
    payload = result.get(field) or {}
    errors = payload.get("errors") or []
    return [str(error) for error in errors]


def _fetch_review_context(
    glab: GlabClient, project_path: str, mr_iid: str
) -> tuple[list[dict[str, Any]], str | None]:
    data = glab.graphql(
        REVIEWERS_QUERY,
        variables={"fullPath": project_path, "iid": mr_iid},
    )
    if not data:
        raise GlabError("graphql reviewers query returned no data")
    mr = (data.get("project") or {}).get("mergeRequest")
    if not mr:
        raise GlabError(f"could not load merge request !{mr_iid} via GraphQL")
    author = (mr.get("author") or {}).get("username")
    reviewers = (mr.get("reviewers") or {}).get("nodes") or []
    return reviewers, author


def _my_review_state(reviewers: list[dict[str, Any]], username: str) -> str | None:
    for reviewer in reviewers:
        if reviewer.get("username") == username:
            interaction = reviewer.get("mergeRequestInteraction") or {}
            return interaction.get("reviewState")
    return None


def _is_reviewer(reviewers: list[dict[str, Any]], username: str) -> bool:
    return any(reviewer.get("username") == username for reviewer in reviewers)


def _append_reviewer(
    glab: GlabClient,
    project_path: str,
    mr_iid: str,
    username: str,
) -> list[str]:
    result = glab.graphql(
        SET_REVIEWERS_MUTATION,
        variables={
            "projectPath": project_path,
            "iid": mr_iid,
            "usernames": [username],
        },
    )
    return _mutation_errors(result, "mergeRequestSetReviewers")


def _request_changes(glab: GlabClient, project_path: str, mr_iid: str) -> list[str]:
    result = glab.graphql(
        REQUEST_CHANGES_MUTATION,
        variables={"projectPath": project_path, "iid": mr_iid},
    )
    return _mutation_errors(result, "mergeRequestRequestChanges")


def _approve(glab: GlabClient, mr_iid: str) -> str | None:
    try:
        glab.api(
            f"projects/:fullpath/merge_requests/{mr_iid}/approve",
            method="POST",
        )
    except GlabError as exc:
        message = str(exc)
        if HTTP_FORBIDDEN_STATUS in message or "forbidden" in message.lower():
            return message
        raise
    return None
