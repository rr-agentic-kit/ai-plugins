"""Unit tests for check, severity_summary, format_markdown."""

from __future__ import annotations

import audit_static as m


def test_check_pass_fail():
    row = m.check("static.test", "major", True, "ok")
    assert row["result"] == "PASS"
    assert row["id"] == "static.test"
    row_fail = m.check("static.test", "major", False, "bad")
    assert row_fail["result"] == "FAIL"


def test_severity_summary():
    results = [
        m.check("a", "critical", True, ""),
        m.check("b", "critical", False, ""),
        m.check("c", "major", True, ""),
    ]
    summary = m.severity_summary(results)
    assert summary["critical"] == {"pass": 1, "total": 2}
    assert summary["major"] == {"pass": 1, "total": 1}


def test_format_markdown_contains_table():
    results = [m.check("static.file.exists", "critical", True, "found")]
    md = m.format_markdown(results, "path.md", "skill")
    assert "## Static checks" in md
    assert "static.file.exists" in md
    assert "Critical: 1/1" in md
