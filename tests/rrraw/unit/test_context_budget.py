"""Unit tests for context_budget token tiers and plan walk."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from context_budget_script import HARD_THRESHOLD, SOFT_THRESHOLD
from context_budget_script.cli import main, run_file, run_plan_dir
from context_budget_script.constants import is_plan_markdown, tier_for
from context_budget_script.tokenize import count_tokens


def test_tier_boundaries() -> None:
    assert tier_for(SOFT_THRESHOLD - 1) == "ok"
    assert tier_for(SOFT_THRESHOLD) == "soft"
    assert tier_for(HARD_THRESHOLD - 1) == "soft"
    assert tier_for(HARD_THRESHOLD) == "hard"


def test_is_plan_markdown() -> None:
    assert is_plan_markdown(Path("/proj/docs/rr/0.1/plan/constitution.md"))
    assert not is_plan_markdown(Path("/proj/docs/rr/0.1/discovery/brd.md"))
    assert not is_plan_markdown(Path("/proj/README.md"))


def test_count_tokens_nonzero() -> None:
    assert count_tokens("hello world") > 0


def _pad_to_tokens(min_tokens: int) -> str:
    """Build text that exceeds min_tokens under cl100k_base."""
    chunk = "word " * 50
    text = chunk
    while count_tokens(text) < min_tokens:
        text += chunk
    return text


def test_file_mode_soft_exit_zero(tmp_path: Path) -> None:
    plan = tmp_path / "docs" / "rr" / "0.1" / "plan"
    plan.mkdir(parents=True)
    path = plan / "architecture.md"
    path.write_text(_pad_to_tokens(SOFT_THRESHOLD), encoding="utf-8")
    code = run_file(path)
    assert code == 0


def test_file_mode_hard_exit_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = tmp_path / "docs" / "rr" / "0.1" / "plan"
    plan.mkdir(parents=True)
    path = plan / "architecture.md"
    path.write_text(_pad_to_tokens(HARD_THRESHOLD), encoding="utf-8")
    code = run_file(path)
    assert code == 1
    out = json.loads(capsys.readouterr().out)
    assert out["files"][0]["tier"] == "hard"
    assert "body" not in out["files"][0]
    assert "content" not in out["files"][0]


def test_plan_dir_walks_and_links(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = tmp_path / "docs" / "rr" / "0.1" / "plan"
    deltas = plan / "deltas"
    deltas.mkdir(parents=True)
    (plan / "constitution.md").write_text(
        "brief\n\nSee [delta](deltas/PRD-1.md).\n", encoding="utf-8"
    )
    (deltas / "PRD-1.md").write_text("feature delta\n", encoding="utf-8")
    code = run_plan_dir(plan)
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    paths = {Path(f["path"]).name for f in out["files"]}
    assert "constitution.md" in paths
    assert "PRD-1.md" in paths


def test_cli_requires_mode() -> None:
    with pytest.raises(SystemExit):
        main([])
