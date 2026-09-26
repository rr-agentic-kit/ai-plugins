"""Unit tests for rr-ci sonar-list-issues --lean reshape."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "rrraw"
    / "skills"
    / "s-ci"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import sonar_list_issues  # noqa: E402


def test_lean_reshape_groups_by_file_omits_issues_and_messages() -> None:
    full = {
        "project": "demo",
        "total": 2,
        "pull_request": "14",
        "issues": [
            {
                "key": "k1",
                "rule": "python:S1",
                "severity": "MAJOR",
                "type": "BUG",
                "file": "src/a.py",
                "line": 3,
                "message": "long message one",
                "status": "OPEN",
            },
            {
                "key": "k2",
                "rule": "python:S2",
                "severity": "MINOR",
                "type": "CODE_SMELL",
                "file": "src/a.py",
                "line": 9,
                "message": "long message two",
                "status": "OPEN",
            },
            {
                "key": "k3",
                "rule": "python:S3",
                "severity": "INFO",
                "type": "CODE_SMELL",
                "file": "src/b.py",
                "line": 1,
                "message": "other",
                "status": "OPEN",
            },
        ],
    }
    lean = sonar_list_issues.lean_reshape(full)
    assert lean["project"] == "demo"
    assert lean["total"] == 2
    assert lean["pull_request"] == "14"
    assert "issues" not in lean
    assert lean["by_file"]["src/a.py"] == [
        {"key": "k1", "rule": "python:S1", "severity": "MAJOR", "line": 3},
        {"key": "k2", "rule": "python:S2", "severity": "MINOR", "line": 9},
    ]
    assert lean["by_file"]["src/b.py"] == [
        {"key": "k3", "rule": "python:S3", "severity": "INFO", "line": 1},
    ]
    for rows in lean["by_file"].values():
        for row in rows:
            assert "message" not in row
