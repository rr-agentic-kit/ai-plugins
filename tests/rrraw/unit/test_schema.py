"""JSON Schema contract vs Python enums."""

from __future__ import annotations

import json

import validate_planning_script as vp


def test_schema_enums_match_python():
    schema = json.loads(vp.SCHEMA_PATH.read_text(encoding="utf-8"))
    defs = schema["$defs"]
    item = defs["item"]["properties"]
    assert set(item["kind"]["enum"]) == set(vp.KIND_VALUES)
    assert set(item["spec"]["enum"]) == set(vp.SPEC_VALUES)
    moscow = {v for v in item["moscow"]["enum"] if v is not None}
    assert moscow == set(vp.MOSCOW_VALUES)
    kano = {v for v in item["kano"]["enum"] if v is not None}
    assert kano == set(vp.KANO_VALUES)
    assert set(item["priority_method"]["enum"]) == set(vp.DOC_METHOD.values())
    assert set(item["impact"]["enum"]) == set(vp.IMPACT_VALUES)
    assert set(item["confidence"]["enum"]) == set(vp.CONFIDENCE_VALUES)
    assert set(item["effort"]["enum"]) == set(vp.EFFORT_VALUES)
    assert set(item["goal_type"]["enum"]) == set(vp.GOAL_TYPE_VALUES)
    assert set(item["id"]["pattern"].split("(")[1].split(")")[0].split("|")) == set(
        vp.PREFIX_TO_DOC
    )
