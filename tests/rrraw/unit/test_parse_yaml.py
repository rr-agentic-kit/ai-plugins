"""YAML doc parse, closed-key drift, format sniff, UNSUPPORTED_FORMAT."""

from __future__ import annotations

import json
from pathlib import Path

import validate_planning as vp
from helpers import VALID_FILES, VALID_YAML_FILES, error_codes, write_planning


def test_parse_yaml_valid_headings():
    items, issues = vp.parse_yaml_doc(VALID_YAML_FILES["prd.yaml"], "prd.yaml")
    assert not error_codes(issues)
    by_id = {item.id: item for item in items}
    assert by_id["PRD-1"].kind == "container"
    assert by_id["PRD-1"].parent == "BRD-1"
    assert by_id["PRD-1.1"].kind == "leaf"
    assert by_id["PRD-1.1"].moscow == "Must"
    assert by_id["PRD-1.1"].spec == "ready"


def test_parse_yaml_triad_axis():
    items, issues = vp.parse_yaml_doc(VALID_YAML_FILES["frd.yaml"], "frd.yaml")
    assert not error_codes(issues)
    leaf = next(item for item in items if item.id == "FRD-1.1")
    assert leaf.build == "in_progress"
    assert leaf.triad is not None
    assert leaf.triad.if_wrong.magnitude == "critical"
    assert leaf.triad.class_name == "must-correct"


def test_yaml_cascade_passes(tmp_path: Path):
    write_planning(tmp_path, VALID_YAML_FILES)
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_yaml_unknown_metadata_key(tmp_path: Path):
    files = {
        "exec-summary.yaml": """\
items:
  ES-1:
    title: Vision
    Parent: —
    Kind: leaf
    Spec: idea
    MoSCoW: —
    Priority: P0
"""
    }
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "UNKNOWN_KEY" in error_codes(issues)


def test_yaml_closed_key_drift(tmp_path: Path):
    write_planning(tmp_path, VALID_YAML_FILES)
    payload = (tmp_path / "items.json").read_text(encoding="utf-8")
    data = json.loads(payload)
    data["items"][0]["title"] = "drifted"
    (tmp_path / "items.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
    issues = vp.validate_dir(tmp_path)
    assert "DRIFT" in error_codes(issues)


def test_mixed_md_yaml_fails(tmp_path: Path):
    write_planning(tmp_path, VALID_FILES)
    (tmp_path / "prd.yaml").write_text(VALID_YAML_FILES["prd.yaml"], encoding="utf-8")
    issues = vp.validate_dir(tmp_path)
    assert "MIXED_FORMAT" in error_codes(issues)


def test_format_flag_selects_yaml_when_mixed(tmp_path: Path):
    write_planning(tmp_path, VALID_YAML_FILES)
    (tmp_path / "prd.md").write_text(VALID_FILES["prd.md"], encoding="utf-8")
    issues = vp.validate_dir(tmp_path, doc_format="yaml")
    assert "MIXED_FORMAT" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_unsupported_format_json(tmp_path: Path):
    write_planning(tmp_path)
    issues = vp.validate_dir(tmp_path, doc_format="json")
    assert "UNSUPPORTED_FORMAT" in error_codes(issues)


def test_cli_json_format_errors(tmp_path: Path):
    write_planning(tmp_path)
    assert vp.main([str(tmp_path), "--format", "json"]) == 1


def test_sniff_yaml_when_only_yaml(tmp_path: Path):
    write_planning(tmp_path, VALID_YAML_FILES)
    fmt, issues = vp.detect_doc_format(tmp_path)
    assert fmt == "yaml"
    assert not error_codes(issues)


def test_yaml_invalid_document(tmp_path: Path):
    files = {"exec-summary.yaml": "- just a list\n"}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "INVALID_YAML" in error_codes(issues)
