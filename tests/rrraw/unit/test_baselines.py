"""Agent-config parse from plugin refs (no planning dir)."""

from __future__ import annotations

import validate_planning_script as vp


def test_parse_agent_config_from_refs():
    version, load_line, body = vp.parse_agent_config()
    assert version == 1
    assert "agent.plan.md" in load_line
    assert "Do not remove this line" in load_line
    template = vp.AGENT_PLAN_TEMPLATE_PATH.read_text(encoding="utf-8")
    assert body == template
    assert "<!-- agent-plan-template -->" not in body
    config = vp.AGENT_CONFIG_PATH.read_text(encoding="utf-8")
    assert "<!-- agent-plan-template -->" not in config
    assert "rrr-status.yaml" in body
    assert "rr-planner" in body
    assert "Do not delete this file" in body
    assert "## Pairing" not in body
    assert "docs/agent.plan.md" in load_line
