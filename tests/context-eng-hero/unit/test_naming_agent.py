"""Unit tests for naming runner (incl. nested agents)."""

from __future__ import annotations

from pathlib import Path

import audit_static as m
from conftest import result_by_id


def test_nested_agent_name_matches_stem(tmp_path: Path):
    root = tmp_path / "plugin"
    agent = root / "agents" / "planning" / "challenge.md"
    agent.parent.mkdir(parents=True)
    agent.write_text(
        "---\n"
        "name: challenge\n"
        "description: Nested agent fixture role for stem match.\n"
        "---\n\n"
        "# challenge\n\n"
        "## Role\n\nCritic.\n\n"
        "## Tools and boundaries\n\n"
        "MUST read docs. MUST NOT write.\n\n"
        "## Stop conditions\n\n"
        "- Done\n"
        "- Failed\n\n"
        "## Inputs\n\nDoc path.\n\n"
        "## Outputs\n\nJSON.\n",
        encoding="utf-8",
    )
    (root / "ACRONYMS.md").write_text(
        "# Acronyms\n\n| Acronym | Expansion | Notes |\n"
        "|---------|-----------|-------|\n| None yet | — | — |\n",
        encoding="utf-8",
    )
    (root / "GLOSSARY.md").write_text(
        "# Glossary\n\n| Term | Meaning (this plugin) | Not confused with | Notes |\n"
        "|------|----------------------|-------------------|-------|\n"
        "| None yet | — | — | — |\n",
        encoding="utf-8",
    )
    results = m.run_checks(root, "agents/planning/challenge.md")
    row = result_by_id(results, "static.name.path-match")
    assert row["result"] == "PASS"


def test_nested_agent_name_mismatch_fails(tmp_path: Path):
    root = tmp_path / "plugin"
    agent = root / "agents" / "planning" / "challenge.md"
    agent.parent.mkdir(parents=True)
    agent.write_text(
        "---\n"
        "name: wrong-name\n"
        "description: Nested agent fixture with wrong name field.\n"
        "---\n\n"
        "# challenge\n\n"
        "## Role\n\nCritic.\n\n"
        "## Tools and boundaries\n\n"
        "MUST read docs. MUST NOT write.\n\n"
        "## Stop conditions\n\n"
        "- Done\n"
        "- Failed\n\n"
        "## Inputs\n\nDoc path.\n\n"
        "## Outputs\n\nJSON.\n",
        encoding="utf-8",
    )
    (root / "ACRONYMS.md").write_text(
        "# Acronyms\n\n| Acronym | Expansion | Notes |\n"
        "|---------|-----------|-------|\n| None yet | — | — |\n",
        encoding="utf-8",
    )
    (root / "GLOSSARY.md").write_text(
        "# Glossary\n\n| Term | Meaning (this plugin) | Not confused with | Notes |\n"
        "|------|----------------------|-------------------|-------|\n"
        "| None yet | — | — | — |\n",
        encoding="utf-8",
    )
    results = m.run_checks(root, "agents/planning/challenge.md")
    row = result_by_id(results, "static.name.path-match")
    assert row["result"] == "FAIL"


def test_detect_nested_agent():
    assert m.detect_type(Path("agents/planning/challenge.md")) == "agent"
