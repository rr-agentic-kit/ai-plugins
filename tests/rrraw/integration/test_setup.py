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
        if parts[0] == "note":
            continue
        result[parts[0]] = (parts[1], parts[2])
    return result


def invoke_setup(
    tmp_path: Path, capsys: object, *, docs: Path | None = None
) -> tuple[int, dict[str, tuple[str, str]]]:
    argv = ["--setup", "--repo-root", str(tmp_path)]
    if docs is not None:
        argv.extend(["--docs-root", str(docs)])
    code = vp.main(argv)
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    return code, parse_setup_out(captured.out)


def test_setup_greenfield(tmp_path: Path, capsys: object) -> None:
    docs = tmp_path / "docs"
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    code, rows = invoke_setup(tmp_path, capsys)
    assert code == 0
    assert rows["docs root"][0] == "created"
    assert rows["discovery directory"][0] == "created"
    assert rows["plan directory"][0] == "created"
    assert rows["root SoT load line"][0] == "fixed"
    assert rows["agent.plan.md"][0] == "created"
    assert rows[vp.RRR_STATUS_NAME][0] == "created"
    assert rows["discovery status.yaml"][0] == "created"
    assert rows["plan status.yaml"][0] == "created"
    assert rows["cascade format"][0] == "ok"
    assert rows["cascade versioning"][0] == "ok"
    assert docs.is_dir()
    assert (docs / "discovery").is_dir()
    assert (docs / "plan").is_dir()
    assert (docs / vp.RRR_STATUS_NAME).is_file()
    assert (docs / "discovery" / "status.yaml").is_file()
    assert (docs / "plan" / "status.yaml").is_file()
    assert (docs / "agent.plan.md").is_file()
    assert not (docs / "future.md").exists()
    for stem in vp.DISCOVERY_STEMS:
        assert not (docs / "discovery" / f"{stem}.md").exists()
    for stem in vp.PLAN_STEMS:
        assert not (docs / "plan" / f"{stem}.md").exists()
    assert not (tmp_path / "AGENTS.md").exists()
    _, load_line, body = vp.parse_agent_config()
    assert "docs/agent.plan.md" in load_line
    assert load_line in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert (docs / "agent.plan.md").read_text(encoding="utf-8") == (
        body if body.endswith("\n") else body + "\n"
    )
    summary, issues = vp.load_status(docs / vp.RRR_STATUS_NAME)
    assert not issues
    assert summary is not None
    assert summary["phase"] == "discovery"
    assert str(summary["track"]) == "0.1"
    assert summary["discovery_complete"] is False
    assert "summary" in summary
    assert "levels" not in summary
    discovery, _ = vp.load_status(docs / "discovery" / "status.yaml")
    assert discovery is not None
    assert set(discovery["levels"]) == set(vp.DISCOVERY_STEMS)
    for doc in vp.DISCOVERY_STEMS:
        assert discovery["levels"][doc]["rev"] == "?"
    assert discovery["mint_hash"] == vp.compute_mint_hash(discovery)
    plan, _ = vp.load_status(docs / "plan" / "status.yaml")
    assert plan is not None
    assert set(plan["levels"]) == set(vp.PLAN_STEMS)
    assert plan["levels"]["prd"]["rev"] == "?"
    assert plan["mint_hash"] == vp.compute_mint_hash(plan)


def test_setup_does_not_create_missing_sot(tmp_path: Path, capsys: object) -> None:
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    invoke_setup(tmp_path, capsys)
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / "GEMINI.md").exists()


def test_setup_stub_version_migration(tmp_path: Path, capsys: object) -> None:
    discovery = tmp_path / "docs" / "discovery"
    discovery.mkdir(parents=True)
    (discovery / "executive-summary.md").write_text(STUB_ES, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    code, rows = invoke_setup(tmp_path, capsys)
    assert code == 0
    assert rows["cascade versioning"][0] == "fixed"
    text = (discovery / "executive-summary.md").read_text(encoding="utf-8")
    fm = vp.parse_frontmatter(text)
    assert "version" not in fm
    assert "traces_from" not in fm
    assert fm["doc_type"] == "executive-summary"
    assert str(fm["track"]) == "0.1"
    assert fm["doc_rev"] in ("?", None)
    status, _ = vp.load_status(discovery / "status.yaml")
    assert status is not None
    assert status["levels"]["executive-summary"]["rev"] == "?"


def test_setup_idempotent_second_run(tmp_path: Path, capsys: object) -> None:
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    first, _ = invoke_setup(tmp_path, capsys)
    assert first == 0
    second, rows = invoke_setup(tmp_path, capsys)
    assert second == 0
    assert {name: status for name, (status, _) in rows.items()} == {
        section: "ok" for section in vp.SETUP_SECTIONS
    }


def test_setup_from0_when_only_statuses(tmp_path: Path, capsys: object) -> None:
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    invoke_setup(tmp_path, capsys)
    docs = tmp_path / "docs"
    assert (docs / vp.RRR_STATUS_NAME).is_file()
    assert (docs / "agent.plan.md").is_file()
    assert not vp.has_cascade_docs(docs / "discovery")
    assert not vp.has_cascade_docs(docs / "plan")


def test_setup_integer_revs_from_existing_status(
    tmp_path: Path, capsys: object
) -> None:
    discovery = tmp_path / "docs" / "discovery"
    write_planning(
        discovery, {"executive-summary.md": VALID_FILES["executive-summary.md"]}
    )
    items = [
        item
        for item in vp.parse_planning_dir(discovery)[0]
        if item.doc == "executive-summary"
    ]
    digest = vp.compute_doc_digest(items, "executive-summary")
    status = vp.default_unfrozen_status(
        vp.parse_agent_config()[0], stems=vp.DISCOVERY_STEMS
    )
    status["levels"]["executive-summary"] = {
        "rev": 2,
        "digest": digest,
        "pins": {},
    }
    status["mint_hash"] = vp.compute_mint_hash(status)
    vp.write_status_yaml(discovery / "status.yaml", status)
    (discovery / "executive-summary.md").write_text(STUB_ES, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    code, _ = invoke_setup(tmp_path, capsys)
    assert code == 0
    fm = vp.parse_frontmatter(
        (discovery / "executive-summary.md").read_text(encoding="utf-8")
    )
    assert fm["doc_rev"] == 2
    reloaded, _ = vp.load_status(discovery / "status.yaml")
    assert reloaded is not None
    assert reloaded["levels"]["executive-summary"]["rev"] == 2
    assert str(reloaded["track"]) == "0.1"


def test_setup_fills_challenge_on_legacy_status(tmp_path: Path, capsys: object) -> None:
    discovery = tmp_path / "docs" / "discovery"
    discovery.mkdir(parents=True)
    status = vp.default_unfrozen_status(
        vp.parse_agent_config()[0], stems=vp.DISCOVERY_STEMS
    )
    recorded = status["mint_hash"]
    del status["challenge"]
    del status["next_challenge"]
    vp.write_status_yaml(discovery / "status.yaml", status)
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    code, _ = invoke_setup(tmp_path, capsys)
    assert code == 0
    reloaded, _ = vp.load_status(discovery / "status.yaml")
    assert reloaded is not None
    assert reloaded["challenge"] == {}
    assert reloaded["next_challenge"] == {}
    assert reloaded["mint_hash"] == recorded
