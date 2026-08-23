"""--setup bootstrap/repair: template path, greenfield, stub-version, idempotence."""

from __future__ import annotations

from pathlib import Path

import validate_planning_script as vp
from helpers import VALID_FILES, write_planning

STUB_ES = """\
---
version: 1
traces_from: none
---

# Exec summary

## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must

> Why now.
"""


def parse_setup_out(out: str) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        result[parts[0]] = (parts[1], parts[2])
    return result


def invoke_setup(
    tmp_path: Path, plans: Path, capsys: object
) -> tuple[int, dict[str, tuple[str, str]]]:
    code = vp.main(["--setup", "--repo-root", str(tmp_path), str(plans)])
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    return code, parse_setup_out(captured.out)


def test_setup_greenfield(tmp_path: Path, capsys: object) -> None:
    plans = tmp_path / "docs" / "plans"
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    code, rows = invoke_setup(tmp_path, plans, capsys)
    assert code == 0
    assert rows["plans directory"][0] == "created"
    assert rows["root SoT load line"][0] == "fixed"
    assert rows["agent.plan.md"][0] == "created"
    assert rows["status.yaml"][0] == "created"
    assert rows["cascade format"][0] == "ok"
    assert rows["cascade versioning"][0] == "ok"
    assert plans.is_dir()
    assert (plans / "status.yaml").is_file()
    assert (plans / "agent.plan.md").is_file()
    assert not (plans / "future.md").exists()
    for stem in vp.DOC_STEMS:
        assert not (plans / f"{stem}.md").exists()
        assert not (plans / f"{stem}.yaml").exists()
    assert not (tmp_path / "AGENTS.md").exists()
    _, load_line, body = vp.parse_agent_config()
    assert load_line in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert (plans / "agent.plan.md").read_text(encoding="utf-8") == (
        body if body.endswith("\n") else body + "\n"
    )
    status, issues = vp.load_status(plans / "status.yaml")
    assert not issues
    assert status is not None
    assert str(status["track"]) == "0.1"
    assert status["product"] == "0.1.0?"
    assert status["docs"] == "0.1.0?"
    assert status["claude_config_version"] == vp.parse_agent_config()[0]
    for doc in vp.DOC_STEMS:
        assert status["levels"][doc]["rev"] == "?"
    assert status["challenge"] == {}
    assert status["next_challenge"] == {}
    assert status["mint_hash"] == vp.compute_mint_hash(status)


def test_setup_does_not_create_missing_sot(tmp_path: Path, capsys: object) -> None:
    plans = tmp_path / "docs" / "plans"
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    invoke_setup(tmp_path, plans, capsys)
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / "GEMINI.md").exists()


def test_setup_stub_version_migration(tmp_path: Path, capsys: object) -> None:
    plans = tmp_path / "docs" / "plans"
    plans.mkdir(parents=True)
    (plans / "exec-summary.md").write_text(STUB_ES, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    code, rows = invoke_setup(tmp_path, plans, capsys)
    assert code == 0
    assert rows["cascade versioning"][0] == "fixed"
    text = (plans / "exec-summary.md").read_text(encoding="utf-8")
    fm = vp.parse_frontmatter(text)
    assert "version" not in fm
    assert "traces_from" not in fm
    assert "version: 1" not in text
    assert "traces_from" not in text
    assert fm["doc_type"] == "exec-summary"
    assert str(fm["track"]) == "0.1"
    assert fm["doc_rev"] in ("?", None)
    assert fm.get("pins") in ({}, None)
    assert "created" in fm
    status, _ = vp.load_status(plans / "status.yaml")
    assert status is not None
    assert status["levels"]["exec-summary"]["rev"] == "?"


def test_setup_idempotent_second_run(tmp_path: Path, capsys: object) -> None:
    plans = tmp_path / "docs" / "plans"
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    first, _ = invoke_setup(tmp_path, plans, capsys)
    assert first == 0
    second, rows = invoke_setup(tmp_path, plans, capsys)
    assert second == 0
    assert {name: status for name, (status, _) in rows.items()} == {
        section: "ok" for section in vp.SETUP_SECTIONS
    }


def test_setup_from0_when_only_status_and_agent_plan(
    tmp_path: Path, capsys: object
) -> None:
    plans = tmp_path / "docs" / "plans"
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    invoke_setup(tmp_path, plans, capsys)
    assert (plans / "status.yaml").is_file()
    assert (plans / "agent.plan.md").is_file()
    assert not vp.has_cascade_docs(plans)


def test_setup_integer_revs_from_existing_status(
    tmp_path: Path, capsys: object
) -> None:
    plans = tmp_path / "docs" / "plans"
    write_planning(plans, {"exec-summary.md": VALID_FILES["exec-summary.md"]})
    items = [
        item for item in vp.parse_planning_dir(plans)[0] if item.doc == "exec-summary"
    ]
    digest = vp.compute_doc_digest(items, "exec-summary")
    status = vp.default_unfrozen_status(vp.parse_agent_config()[0])
    status["levels"]["exec-summary"] = {
        "rev": 2,
        "digest": digest,
        "pins": {},
    }
    status["mint_hash"] = vp.compute_mint_hash(status)
    vp.write_status_yaml(plans / "status.yaml", status)
    (plans / "exec-summary.md").write_text(STUB_ES, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    code, _ = invoke_setup(tmp_path, plans, capsys)
    assert code == 0
    fm = vp.parse_frontmatter((plans / "exec-summary.md").read_text(encoding="utf-8"))
    assert fm["doc_rev"] == 2
    reloaded, _ = vp.load_status(plans / "status.yaml")
    assert reloaded is not None
    assert reloaded["levels"]["exec-summary"]["rev"] == 2
    assert str(reloaded["track"]) == "0.1"


def test_setup_fills_challenge_on_legacy_status(tmp_path: Path, capsys: object) -> None:
    plans = tmp_path / "docs" / "plans"
    plans.mkdir(parents=True)
    status = vp.default_unfrozen_status(vp.parse_agent_config()[0])
    recorded = status["mint_hash"]
    del status["challenge"]
    del status["next_challenge"]
    vp.write_status_yaml(plans / "status.yaml", status)
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    code = vp.main(["--setup", "--repo-root", str(tmp_path), str(plans)])
    capsys.readouterr()
    assert code == 0
    reloaded, _ = vp.load_status(plans / "status.yaml")
    assert reloaded is not None
    assert reloaded["challenge"] == {}
    assert reloaded["next_challenge"] == {}
    assert reloaded["mint_hash"] == recorded
