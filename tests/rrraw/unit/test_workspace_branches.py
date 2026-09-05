"""Unit tests for validate_planning_script.workspace uncovered branches."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from validate_planning_script import workspace as ws


def test_resolve_within_root_rejects_escape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(ValueError, match="outside repo root"):
        ws.resolve_within_root(outside, repo)


def test_planning_doc_path_invalid_stem(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="invalid planning doc stem"):
        ws.planning_doc_path(tmp_path, "not-a-doc")


def test_load_status_invalid_yaml(tmp_path: Path) -> None:
    path = tmp_path / "status.yaml"
    path.write_text("track: [\n", encoding="utf-8")
    data, issues = ws.load_status(path)
    assert data is None
    assert issues[0].code == "HAND_BUMP"


def test_load_status_not_mapping(tmp_path: Path) -> None:
    path = tmp_path / "status.yaml"
    path.write_text("- list\n", encoding="utf-8")
    data, issues = ws.load_status(path)
    assert data is None
    assert "mapping" in issues[0].message


def test_challenge_map_replaces_non_dict() -> None:
    status: dict = {"challenge": "bogus"}
    result = ws.challenge_map(status)
    assert result == {}
    assert status["challenge"] == {}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", None),
        ("  ", None),
        ("prd.md § goals", "prd"),
        ("unknown.md", None),
        (42, None),
    ],
)
def test_challenge_doc_stem(value: object, expected: str | None) -> None:
    assert ws.challenge_doc_stem(value) == expected


def test_invalidate_challenge_on_compose_marks_dirty() -> None:
    status = ws.default_unfrozen_status(1)
    status["challenge"]["prd"] = {
        "status": "clean",
        "scanned_digest": "sha256:old",
    }
    ws.invalidate_challenge_on_compose(status, "prd")
    assert status["challenge"]["prd"]["status"] == "dirty"


def test_invalidate_challenge_on_digest_change() -> None:
    status = ws.default_unfrozen_status(1)
    status["levels"]["prd"]["digest"] = "sha256:new"
    status["challenge"]["prd"] = {
        "status": "clean",
        "scanned_digest": "sha256:old",
    }
    ws.invalidate_challenge_on_digest_change(status)
    assert status["challenge"]["prd"]["status"] == "dirty"


def test_accept_challenge_residual_sets_dirty_accepted() -> None:
    status = ws.default_unfrozen_status(1)
    status["levels"]["prd"]["digest"] = "sha256:prd"
    ws.accept_challenge_residual(status, ["prd"])
    assert status["challenge"]["prd"]["status"] == "dirty-accepted"
    assert status["challenge"]["prd"]["scanned_digest"] == "sha256:prd"


def test_ensure_doc_frontmatter_creates_missing_keys() -> None:
    text = "# Exec summary\n\nBody.\n"
    new_text, outcome = ws.ensure_doc_frontmatter(text, "executive-summary", None)
    assert outcome == "created"
    assert new_text.startswith("---\n")
    assert "doc_type: executive-summary" in new_text


def test_ensure_doc_frontmatter_ok_when_unchanged() -> None:
    status = ws.default_unfrozen_status(1)
    text, _ = ws.ensure_doc_frontmatter("# Body\n", "executive-summary", status)
    new_text, outcome = ws.ensure_doc_frontmatter(text, "executive-summary", status)
    assert outcome == "ok"
    assert new_text == text


def test_maturity_preserved_and_freeze_blocked() -> None:
    status = ws.default_unfrozen_status(1, stems=("executive-summary",))
    status["levels"]["executive-summary"]["maturity"] = "code-extraction"
    text, outcome = ws.ensure_doc_frontmatter("# Body\n", "executive-summary", status)
    assert "maturity: code-extraction" in text
    assert outcome in {"created", "fixed", "ok"}
    issues = ws._check_maturity(
        "executive-summary",
        status["levels"],
        {"executive-summary": {"maturity": "code-extraction", "doc_rev": "?"}},
        "?",
    )
    assert issues == []
    frozen = ws._check_maturity(
        "executive-summary",
        {"executive-summary": {"maturity": "code-extraction", "rev": 1}},
        {"executive-summary": {"maturity": "code-extraction"}},
        1,
    )
    assert any(i.code == "CODE_EXTRACTION_FROZEN" for i in frozen)
    bad = ws._check_maturity(
        "executive-summary",
        {"executive-summary": {"maturity": "ready"}},
        {},
        "?",
    )
    assert any(i.code == "INVALID_MATURITY" for i in bad)


def test_frontmatter_pins_from_frozen_parent() -> None:
    levels = {
        "brd": {"rev": 2, "digest": "sha256:brd"},
        "prd": {
            "rev": "?",
            "pins": {"brd": {"rev": 2, "digest": "sha256:brd-pin"}},
        },
    }
    pins = ws._frontmatter_pins("prd", levels)
    assert pins["brd"]["rev"] == 2
    assert pins["brd"]["digest"] == "sha256:brd-pin"


def test_levels_for_dir_next_track(tmp_path: Path) -> None:
    status = ws.default_unfrozen_status(1)
    status["next"] = "0.2"
    status["next_levels"] = {"prd": {"rev": "?", "digest": None, "pins": {}}}
    track_dir = tmp_path / "0.2"
    track_dir.mkdir()
    levels = ws._levels_for_dir(status, track_dir)
    assert "prd" in levels


def test_load_frozen_levels_from_session_state(tmp_path: Path) -> None:
    payload = {"frozen_levels": ["prd", "brd"]}
    (tmp_path / "session-state.json").write_text(json.dumps(payload), encoding="utf-8")
    assert ws._load_frozen_levels(tmp_path) == ["prd", "brd"]


def test_load_frozen_levels_invalid_json(tmp_path: Path) -> None:
    (tmp_path / "session-state.json").write_text("{bad", encoding="utf-8")
    assert ws._load_frozen_levels(tmp_path) is None


def test_docs_root_and_rrr_status(tmp_path: Path) -> None:
    docs = ws.docs_root(tmp_path)
    assert docs == tmp_path / "docs"
    assert ws.find_rrr_status_path(docs) is None
    (docs).mkdir()
    path = docs / "rrr-status.yaml"
    path.write_text("track: '0.1'\n", encoding="utf-8")
    assert ws.find_rrr_status_path(docs) == path
    summary = ws.default_rrr_status(1)
    assert summary["phase"] == "discovery"
    assert "levels" not in summary


def test_stems_for_phase_dirs(tmp_path: Path) -> None:
    discovery = tmp_path / "discovery"
    plan = tmp_path / "plan"
    discovery.mkdir()
    plan.mkdir()
    assert ws.stems_for_dir(discovery) == ("executive-summary", "mrd", "brd")
    assert ws.stems_for_dir(plan) == ("prd",)
    assert ws.stems_for_dir(tmp_path) == (
        "executive-summary",
        "mrd",
        "brd",
        "prd",
    )
