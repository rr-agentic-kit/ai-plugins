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
    assert by_id["PRD-1.1"].moscow == "Must"
    assert by_id["PRD-1.1"].spec == "ready"


def test_parse_yaml_triad_axis_migrate_reader():
    items, issues = vp.parse_yaml_doc(VALID_YAML_FILES["frd.yaml"], "frd.yaml")
    assert not error_codes(issues)
    leaf = next(item for item in items if item.id == "FRD-1.1")
    assert leaf.build == "in_progress"
    assert leaf.triad is not None
    assert leaf.triad.if_wrong.magnitude == "critical"
    assert leaf.triad.class_name == "must-correct"


def test_parse_yaml_invalid_root():
    items, issues = vp.parse_yaml_doc("- just a list\n", "exec-summary.yaml")
    assert items == []
    assert "INVALID_YAML" in error_codes(issues)
