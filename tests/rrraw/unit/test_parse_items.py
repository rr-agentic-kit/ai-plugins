"""Parser and closed-vocabulary tests (string-level)."""

from __future__ import annotations

import validate_planning_script as vp
from helpers import VALID_FILES, error_codes


def test_parse_valid_headings():
    items, issues = vp.parse_markdown(VALID_FILES["prd.md"], "prd.md")
    assert not error_codes(issues)
    by_id = {item.id: item for item in items}
    assert by_id["PRD-1"].kind == "container"
    assert by_id["PRD-1"].parent == "BRD-1"
    assert by_id["PRD-1.1"].kind == "leaf"
    assert by_id["PRD-1.1"].reach == "40% of monthly active users"
    assert by_id["PRD-1.1"].impact == "2"
    assert by_id["PRD-1.1"].spec == "ready"


def test_parse_unranked_em_dash():
    text = """\
## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: idea | _moscow_: —
"""
    items, _ = vp.parse_markdown(text, "executive-summary.md")
    leaf = items[0]
    assert leaf.parent is None
    assert leaf.moscow is None
    assert leaf.spec == "idea"


def test_parse_prd_status():
    text = """\
## PRD-1.1: Guest checkout
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _reach_: 40% of monthly active users | _impact_: 2 | _confidence_: medium | _effort_: 5 | _status_: delivered
"""
    items, issues = vp.parse_markdown(text, "prd.md")
    assert not error_codes(issues)
    leaf = items[0]
    assert leaf.status == "delivered"


def test_pipe_in_meta_value_does_not_split_keys():
    text = """\
## PRD-1.1: Guest checkout
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _reach_: 40% of monthly active users | _impact_: 2 | _confidence_: medium | _effort_: 5 | _status_: in_progress | shipped
"""
    items, issues = vp.parse_markdown(text, "prd.md")
    assert "MALFORMED_META" not in error_codes(issues)
    leaf = items[0]
    assert leaf.status == "in_progress | shipped"
    assert "INVALID_VALUE" in error_codes(issues)


def test_unknown_metadata_key():
    text = """\
## ES-1: Vision
_parent_: — | _kind_: leaf | _spec_: idea | _moscow_: — | _foo_: bar
"""
    _, issues = vp.parse_markdown(text, "executive-summary.md")
    assert "UNKNOWN_KEY" in error_codes(issues)


def test_priority_on_es_unknown_value_or_scope():
    text = """\
## ES-1: Vision
_parent_: — | _kind_: leaf | _spec_: idea | _moscow_: Must | _priority_: P0
"""
    items, issues = vp.parse_markdown(text, "executive-summary.md")
    assert "INVALID_VALUE" in error_codes(issues)
    scope = vp.check_required_fields(items)
    # P0 fails enum before scope; valid P1 on ES still fails scope
    text_p1 = """\
## ES-1: Vision
_parent_: — | _kind_: leaf | _spec_: idea | _moscow_: Must | _priority_: P1
"""
    items_p1, parse_issues = vp.parse_markdown(text_p1, "executive-summary.md")
    assert not error_codes(parse_issues)
    assert "PRIORITY_SCOPE" in error_codes(vp.check_required_fields(items_p1))
    _ = scope


def test_missing_required_key():
    text = """\
## ES-1: Vision
_kind_: leaf | _spec_: idea | _moscow_: —
"""
    _, issues = vp.parse_markdown(text, "executive-summary.md")
    assert "MISSING_KEY" in error_codes(issues)


def test_malformed_meta_line():
    text = """\
## ES-1: Vision
Parent: none
"""
    _, issues = vp.parse_markdown(text, "executive-summary.md")
    assert "MALFORMED_META" in error_codes(issues)


def test_stale_list_meta():
    text = """\
## ES-1: Vision
- **Parent:** —
- **Kind:** leaf
- **Spec:** idea
- **MoSCoW:** —
"""
    _, issues = vp.parse_markdown(text, "executive-summary.md")
    assert "STALE_FORMAT" in error_codes(issues)


def test_body_not_blockquote():
    text = """\
## ES-1: Vision
_parent_: — | _kind_: leaf | _spec_: idea | _moscow_: —

Vision without quotes.
"""
    _, issues = vp.parse_markdown(text, "executive-summary.md")
    assert "BODY_NOT_BLOCKQUOTE" in error_codes(issues)


def test_invalid_rationale_shape():
    text = """\
## PRD-1.1: Guest checkout
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _reach_: 40% of monthly active users | _impact_: 2 | _confidence_: medium | _effort_: 5 | _rationale_: rationale-4
"""
    _, issues = vp.parse_markdown(text, "prd.md")
    assert "INVALID_VALUE" in error_codes(issues)


def test_parse_inline_meta_duplicate_key():
    meta, errors = vp.parse_inline_meta_line(
        "_parent_: — | _kind_: leaf | _kind_: container | _spec_: idea"
    )
    assert ("DUPLICATE_KEY", "kind") in errors
    assert meta["kind"] == "container"


def test_parse_missing_metadata_line():
    text = """\
## ES-1: Vision
"""
    _, issues = vp.parse_markdown(text, "executive-summary.md")
    assert "MALFORMED_META" in error_codes(issues)


def test_parse_list_meta_unknown_key():
    text = """\
## ES-1: Vision
- **Parent:** —
- **Kind:** leaf
- **Spec:** idea
- **MoSCoW:** —
- **Foo:** bar
"""
    _, issues = vp.parse_markdown(text, "executive-summary.md", migrate=True)
    assert "UNKNOWN_KEY" in error_codes(issues)


def test_parse_list_meta_duplicate_key():
    text = """\
## ES-1: Vision
- **Kind:** leaf
- **Kind:** container
- **Parent:** —
- **Spec:** idea
- **MoSCoW:** —
"""
    _, issues = vp.parse_markdown(text, "executive-summary.md", migrate=True)
    assert "DUPLICATE_KEY" in error_codes(issues)
