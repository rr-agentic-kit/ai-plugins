"""Issue formatting, has_errors, format_meta_line."""

from __future__ import annotations

import validate_planning_script as vp


def test_issue_format_error_and_warn():
    assert vp.Issue.error("X", "msg", "ES-1").format() == "ERROR [X] ES-1: msg"
    assert vp.Issue.warn("Y", "w").format() == "WARN [Y]: w"


def test_has_errors():
    assert vp.has_errors([vp.Issue.warn("Y", "w")]) is False
    assert vp.has_errors([vp.Issue.error("X", "m")]) is True
    assert vp.has_errors([]) is False


def test_format_meta_line_omits_rank():
    line = vp.format_meta_line({"parent": "—", "kind": "leaf", "spec": "idea"})
    assert line == "_parent_: — | _kind_: leaf | _spec_: idea"
    assert "_moscow_" not in line
    assert "_kano_" not in line
