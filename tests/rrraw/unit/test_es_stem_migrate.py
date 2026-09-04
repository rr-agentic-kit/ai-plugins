"""Stem migration: exec-summary → executive-summary."""

from __future__ import annotations

from pathlib import Path

import validate_planning_script as vp
import yaml


def test_canonicalize_doc_stem() -> None:
    assert vp.canonicalize_doc_stem("exec-summary") == "executive-summary"
    assert vp.canonicalize_doc_stem("executive-summary") == "executive-summary"
    assert vp.canonicalize_doc_stem("mrd") == "mrd"


def test_migrate_exec_summary_stem(tmp_path: Path) -> None:
    from validate_planning_script import shape_migrate

    (tmp_path / "exec-summary.md").write_text(
        "---\ndoc_type: exec-summary\n---\n# ES\n",
        encoding="utf-8",
    )
    status = {
        "track": "0.1",
        "levels": {
            "exec-summary": {"rev": 1, "digest": "sha256:abc", "pins": {}},
            "mrd": {
                "rev": "?",
                "digest": None,
                "pins": {"exec-summary": {"rev": 1, "digest": "sha256:abc"}},
            },
        },
        "challenge": {"exec-summary": {"status": "dirty", "depth": None}},
    }
    (tmp_path / "status.yaml").write_text(
        yaml.safe_dump(status, sort_keys=False),
        encoding="utf-8",
    )
    issues = shape_migrate.migrate_exec_summary_stem(tmp_path)
    assert any(i.code == "MIGRATE_ES_STEM" for i in issues)
    assert (tmp_path / "executive-summary.md").is_file()
    assert not (tmp_path / "exec-summary.md").exists()
    text = (tmp_path / "executive-summary.md").read_text(encoding="utf-8")
    assert "doc_type: executive-summary" in text
    loaded = yaml.safe_load((tmp_path / "status.yaml").read_text(encoding="utf-8"))
    assert "executive-summary" in loaded["levels"]
    assert "exec-summary" not in loaded["levels"]
    assert "executive-summary" in loaded["levels"]["mrd"]["pins"]
    assert "executive-summary" in loaded["challenge"]


def test_schema_path_points_at_shared_refs() -> None:
    assert vp.SCHEMA_PATH.is_file()
    assert "refs/planning/schemas" in str(vp.SCHEMA_PATH).replace("\\", "/")
    assert vp.AGENT_CONFIG_PATH.is_file()
    assert "refs/planning/agent-config.md" in str(vp.AGENT_CONFIG_PATH).replace(
        "\\", "/"
    )
