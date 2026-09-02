"""Unit tests for validate_planning_script.setup error and edge branches."""

from __future__ import annotations

from pathlib import Path

import pytest
from validate_planning_script import setup as setup_mod


def test_parse_agent_config_missing_fence() -> None:
    with pytest.raises(ValueError, match="missing injection yaml fence"):
        setup_mod.parse_agent_config("no fence here")


def test_parse_agent_config_injection_not_mapping() -> None:
    text = """\
```yaml
injection: not-a-mapping
```
"""
    with pytest.raises(ValueError, match="injection must be a mapping"):
        setup_mod.parse_agent_config(text)


def test_parse_agent_config_invalid_version() -> None:
    text = """\
```yaml
injection:
  version: zero
  load_line: "load docs/plans"
```
"""
    with pytest.raises(ValueError, match="version must be a positive int"):
        setup_mod.parse_agent_config(text)


def test_setup_plans_directory_when_path_is_file(tmp_path: Path) -> None:
    blocker = tmp_path / "plans"
    blocker.write_text("not a dir", encoding="utf-8")
    status, message = setup_mod.setup_plans_directory(blocker, tmp_path)
    assert status == "failed"
    assert "is a file" in message


def test_setup_plans_directory_exists(tmp_path: Path) -> None:
    plans = tmp_path / "docs" / "plans"
    plans.mkdir(parents=True)
    status, message = setup_mod.setup_plans_directory(plans, tmp_path)
    assert status == "ok"
    assert message == "exists"


def test_setup_root_sot_no_files(tmp_path: Path) -> None:
    status, message = setup_mod.setup_root_sot(tmp_path, "load line")
    assert status == "ok"
    assert message == "no root SoT files"


def test_setup_agent_plan_overwrites_mismatch(tmp_path: Path) -> None:
    plans = tmp_path / "plans"
    plans.mkdir()
    body = "# Planning pairing\n\nTemplate body.\n"
    (plans / "agent.plan.md").write_text("# stale\n", encoding="utf-8")
    status, message = setup_mod.setup_agent_plan(plans, body)
    assert status == "fixed"
    assert message == "overwrote to template"
    assert (plans / "agent.plan.md").read_text(encoding="utf-8") == body


def test_setup_status_invalid_yaml(tmp_path: Path) -> None:
    plans = tmp_path / "plans"
    plans.mkdir()
    (plans / "status.yaml").write_text("not: [valid", encoding="utf-8")
    status, message = setup_mod.setup_status(plans, 1)
    assert status == "failed"
    assert "status.yaml" in message.lower() or "mapping" in message.lower()


def test_setup_cascade_format_not_directory(tmp_path: Path) -> None:
    blocker = tmp_path / "plans"
    blocker.write_text("file", encoding="utf-8")
    status, message = setup_mod.setup_cascade_format(blocker)
    assert status == "failed"
    assert "not a directory" in message


def test_setup_cascade_versioning_yaml_read_error(tmp_path: Path) -> None:
    plans = tmp_path / "plans"
    plans.mkdir()
    (plans / "exec-summary.md").write_text(
        "---\nversion: [unclosed\n---\n# Body\n", encoding="utf-8"
    )
    status, message = setup_mod.setup_cascade_versioning(plans)
    assert status == "failed"
    assert "exec-summary.md" in message


def test_sync_agent_injection_parse_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plans = tmp_path / "plans"
    plans.mkdir()
    (plans / "status.yaml").write_text("track: 0.1\n", encoding="utf-8")

    def _broken() -> tuple[int, str, str]:
        raise ValueError("broken config")

    monkeypatch.setattr(setup_mod, "parse_agent_config", _broken)
    issues = setup_mod.sync_agent_injection(plans, tmp_path, force=True)
    assert len(issues) == 1
    assert issues[0].code == "HAND_BUMP"


def test_run_setup_plans_outside_repo(tmp_path: Path, capsys: object) -> None:
    outside = tmp_path / "outside" / "plans"
    outside.mkdir(parents=True)
    repo = tmp_path / "repo"
    repo.mkdir()
    code = setup_mod.run_setup(outside, repo)
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert code == 1
    assert "outside repo root" in captured.out
