"""JSON Schema contract vs Python enums, CLI exit codes."""

from __future__ import annotations

import json
from pathlib import Path

import validate_planning as vp
from helpers import error_codes, write_planning


def test_schema_enums_match_python():
    schema = json.loads(vp.SCHEMA_PATH.read_text(encoding="utf-8"))
    defs = schema["$defs"]
    item = defs["item"]["properties"]
    assert set(item["kind"]["enum"]) == set(vp.KIND_VALUES)
    assert set(item["spec"]["enum"]) == set(vp.SPEC_VALUES)
    assert set(item["build"]["enum"]) == set(vp.BUILD_VALUES)
    moscow = {v for v in item["moscow"]["enum"] if v is not None}
    assert moscow == set(vp.MOSCOW_VALUES)
    kano = {v for v in item["kano"]["enum"] if v is not None}
    assert kano == set(vp.KANO_VALUES)
    assert set(defs["magnitude"]["enum"]) == set(vp.MAGNITUDE_VALUES)
    assert set(defs["triad"]["properties"]["class"]["enum"]) == set(vp.CLASS_VALUES)
    assert set(item["id"]["pattern"].split("(")[1].split(")")[0].split("|")) == set(
        vp.PREFIX_TO_DOC
    )


def test_cli_ok(tmp_path: Path):
    write_planning(tmp_path)
    assert vp.main([str(tmp_path)]) == 0


def test_cli_fail(tmp_path: Path):
    write_planning(tmp_path, write_json=False)
    assert vp.main([str(tmp_path)]) == 1


def test_cli_missing_dir(tmp_path: Path):
    assert vp.main([str(tmp_path / "nope")]) == 1


def test_missing_items_json(tmp_path: Path):
    write_planning(tmp_path, write_json=False)
    issues = vp.validate_dir(tmp_path)
    assert "MISSING_JSON" in error_codes(issues)


def test_extra_json_key(tmp_path: Path):
    write_planning(tmp_path)
    payload = json.loads((tmp_path / "items.json").read_text(encoding="utf-8"))
    payload["items"][0]["traces_to"] = "ES-1"
    (tmp_path / "items.json").write_text(json.dumps(payload), encoding="utf-8")
    issues = vp.validate_dir(tmp_path)
    assert "UNKNOWN_KEY" in error_codes(issues)
