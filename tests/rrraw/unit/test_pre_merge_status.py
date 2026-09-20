"""Unit tests for rr-ci pre-merge-status verdict assembly."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "rrraw"
    / "skills"
    / "rr-ci"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import pre_merge_status  # noqa: E402


def test_assemble_verdict_ready() -> None:
    result = pre_merge_status.assemble_verdict(
        {
            "pipeline": {"status": "success"},
            "security": {"status": "clean", "merge_blocked": False},
            "unresolved_threads": 0,
            "reviews": {
                "approvals_left": 0,
                "approvals_required": 1,
                "approved": True,
                "summary": "approved",
            },
            "has_conflicts": False,
        }
    )
    assert result["verdict"] == "ready"
    assert result["blockers"] == []
    assert result["unresolved_threads"] == 0


def test_assemble_verdict_blocked_pipeline_and_threads() -> None:
    result = pre_merge_status.assemble_verdict(
        {
            "pipeline": {"status": "failed"},
            "security": {"merge_blocked": True, "status": "blocking_findings"},
            "unresolved_threads": 2,
            "reviews": {"approvals_left": 1, "summary": "left=1"},
            "has_conflicts": True,
        }
    )
    assert result["verdict"] == "blocked"
    assert "pipeline:failed" in result["blockers"]
    assert "has_conflicts" in result["blockers"]
    assert "security_merge_blocked" in result["blockers"]
    assert "unresolved_threads:2" in result["blockers"]
    assert "approvals_left:1" in result["blockers"]


def test_assemble_verdict_pending_pipeline() -> None:
    result = pre_merge_status.assemble_verdict(
        {
            "pipeline": {"status": "running"},
            "security": {"merge_blocked": False},
            "unresolved_threads": 0,
            "reviews": {},
        }
    )
    assert result["verdict"] == "blocked"
    assert result["blockers"] == ["pipeline_pending:running"]
