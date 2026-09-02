"""YAML ingest (string-level)."""

from __future__ import annotations

import validate_planning_script as vp
from helpers import VALID_YAML_FILES, error_codes


def test_parse_yaml_valid_headings_migrate_reader():
    items, issues = vp.parse_yaml_doc(VALID_YAML_FILES["prd.yaml"], "prd.yaml")
    assert not error_codes(issues)
    by_id = {item.id: item for item in items}
    assert by_id["PRD-1"].kind == "container"
    assert by_id["PRD-1"].parent == "BRD-1"
    assert by_id["PRD-1.1"].kind == "leaf"
    assert by_id["PRD-1.1"].reach == "40% of monthly active users"
    assert by_id["PRD-1.1"].impact == "2"
    assert by_id["PRD-1.1"].spec == "ready"


def test_parse_yaml_prd_status_migrate_reader():
    yaml_text = """\
doc_type: prd
title: PRD
items:
  PRD-1.1:
    title: Guest checkout
    Parent: PRD-1
    Kind: leaf
    Spec: ready
    Reach: 40% of monthly active users
    Impact: "2"
    Confidence: medium
    Effort: "5"
    Status: delivered
"""
    items, issues = vp.parse_yaml_doc(yaml_text, "prd.yaml")
    assert not error_codes(issues)
    leaf = next(item for item in items if item.id == "PRD-1.1")
    assert leaf.status == "delivered"


def test_parse_inline_meta_empty_line():
    meta, errors = vp.parse_inline_meta_line("   ")
    assert meta == {}
    assert errors == [("MALFORMED_META", "   ")]


def test_parse_inline_meta_unknown_key():
    _, errors = vp.parse_inline_meta_line("_parent_: — | _unknown_: x")
    assert ("UNKNOWN_KEY", "unknown") in errors


def test_parse_yaml_empty_doc():
    items, issues = vp.parse_yaml_doc("", "exec-summary.yaml")
    assert items == []
    assert issues == []


def test_parse_yaml_item_not_mapping():
    yaml_text = """\
items:
  ES-1: not-a-mapping
"""
    items, issues = vp.parse_yaml_doc(yaml_text, "exec-summary.yaml")
    assert items == []
    assert "INVALID_YAML" in error_codes(issues)


def test_parse_yaml_unknown_key():
    yaml_text = """\
items:
  ES-1:
    title: Vision
    UnknownKey: value
    Parent: —
    Kind: leaf
    Spec: idea
    MoSCoW: —
"""
    _, issues = vp.parse_yaml_doc(yaml_text, "exec-summary.yaml")
    assert "UNKNOWN_KEY" in error_codes(issues)


def test_parse_yaml_invalid_root():
    items, issues = vp.parse_yaml_doc("- just a list\n", "exec-summary.yaml")
    assert items == []
    assert "INVALID_YAML" in error_codes(issues)


def test_parse_yaml_invalid_id():
    yaml_text = """\
items:
  BAD:
    title: Bad id
    Parent: —
    Kind: leaf
    Spec: idea
    MoSCoW: —
"""
    items, issues = vp.parse_yaml_doc(yaml_text, "exec-summary.yaml")
    assert items == []
    assert "INVALID_ID" in error_codes(issues)
