"""Unit tests for audit_static.models.AuditContext."""

from __future__ import annotations

from pathlib import Path

import pytest
from audit_static.models import MAX_READ_BYTES, AuditContext


def _minimal_skill_content() -> str:
    return (
        "---\n"
        "name: test-skill\n"
        "description: A test skill for AuditContext.load.\n"
        "---\n\n"
        "# Test\n"
    )


def test_audit_context_load_happy_path(tmp_path: Path) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    rel_path = "skills/test-skill/SKILL.md"
    skill_path = plugin_root / rel_path
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text(_minimal_skill_content(), encoding="utf-8")
    # Act
    loaded = AuditContext.load(plugin_root, rel_path)
    # Assert
    assert isinstance(loaded, AuditContext)
    assert loaded.rel_path == rel_path
    assert loaded.artifact_type == "skill"
    assert loaded.fm is not None
    assert loaded.fm["name"] == "test-skill"
    assert loaded.body.startswith("# Test")


def test_audit_context_load_path_outside_plugin(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    plugin_root.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("secret", encoding="utf-8")
    read_called = False
    original_read_text = Path.read_text

    def tracking_read_text(self: Path, *args, **kwargs):
        nonlocal read_called
        read_called = True
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", tracking_read_text)
    # Act
    result = AuditContext.load(plugin_root, "../outside.md")
    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "static.paths.within-plugin"
    assert result[0]["severity"] == "critical"
    assert result[0]["result"] == "FAIL"
    assert not read_called


def test_audit_context_load_missing_file(tmp_path: Path) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    plugin_root.mkdir()
    # Act
    result = AuditContext.load(plugin_root, "skills/missing/SKILL.md")
    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "static.file.exists"
    assert result[0]["result"] == "FAIL"
    assert "file not found" in result[0]["evidence"]


def test_audit_context_load_oversize_file(tmp_path: Path) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    rel_path = "skills/big/SKILL.md"
    skill_path = plugin_root / rel_path
    skill_path.parent.mkdir(parents=True)
    with skill_path.open("wb") as handle:
        handle.truncate(MAX_READ_BYTES + 1)
    # Act
    result = AuditContext.load(plugin_root, rel_path)
    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "static.file.size"
    assert result[0]["result"] == "FAIL"
    assert "exceeds size cap" in result[0]["evidence"]
