"""Unit tests for audit_static.links module."""

from __future__ import annotations

from pathlib import Path

import pytest
from audit_static.links import (
    collect_broken_links,
    collect_insecure_http_links,
    link_scheme,
    resolve_link,
)
from audit_static.models import AuditContext


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("https://example.com", "https"),
        ("http://example.com", "http"),
        ("mailto:user@example.com", "mailto"),
        ("file:///tmp/foo", "file"),
        ("refs/foo.md", None),
        ("#anchor", None),
        ("", None),
    ],
)
def test_link_scheme(target: str, expected: str | None) -> None:
    # Arrange — target is a markdown link destination
    # Act
    result = link_scheme(target)
    # Assert
    assert result == expected


def test_resolve_link_in_bounds_relative(tmp_path: Path) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    skill_dir = plugin_root / "skills" / "foo" / "refs"
    skill_dir.mkdir(parents=True)
    source = plugin_root / "skills" / "foo" / "SKILL.md"
    source.write_text("# skill\n", encoding="utf-8")
    (skill_dir / "bar.md").write_text("# bar\n", encoding="utf-8")
    # Act
    resolved = resolve_link(plugin_root, source, "refs/bar.md")
    # Assert
    assert resolved is True


def test_resolve_link_escapes_plugin_root(tmp_path: Path) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    outside = tmp_path / "outside.md"
    outside.write_text("# outside\n", encoding="utf-8")
    source_dir = plugin_root / "skills" / "foo"
    source_dir.mkdir(parents=True)
    source = source_dir / "SKILL.md"
    source.write_text("# skill\n", encoding="utf-8")
    # Act
    resolved = resolve_link(plugin_root, source, "../../../outside.md")
    # Assert
    assert resolved is False


def test_resolve_link_absolute_url_skipped(tmp_path: Path) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    plugin_root.mkdir()
    source = plugin_root / "SKILL.md"
    source.write_text("# skill\n", encoding="utf-8")
    # Act
    resolved = resolve_link(plugin_root, source, "https://example.com")
    # Assert
    assert resolved is True


def _make_link_ctx(plugin_root: Path, rel_path: str, body: str) -> AuditContext:
    target = plugin_root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# placeholder\n", encoding="utf-8")
    return AuditContext(
        plugin_root=plugin_root,
        rel_path=rel_path,
        rel=Path(rel_path),
        target=target,
        text="",
        artifact_type="skill",
        body=body,
        fm=None,
        fm_err=None,
        has_fm=False,
    )


def test_collect_broken_links(tmp_path: Path) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    docs_dir = plugin_root / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "exists.md").write_text("# ok\n", encoding="utf-8")
    ctx = _make_link_ctx(
        plugin_root,
        "skills/foo/SKILL.md",
        "See [ok](../../docs/exists.md) and [bad](refs/missing.md).\n",
    )
    # Act
    broken = collect_broken_links(ctx)
    # Assert
    assert "refs/missing.md" in broken
    assert "../../docs/exists.md" not in broken


def test_collect_insecure_http_links(tmp_path: Path) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    plugin_root.mkdir()
    ctx = AuditContext(
        plugin_root=plugin_root,
        rel_path="skills/foo/SKILL.md",
        rel=Path("skills/foo/SKILL.md"),
        target=plugin_root / "skills/foo/SKILL.md",
        text="",
        artifact_type="skill",
        body="[insecure](http://example.com) [secure](https://example.com)\n",
        fm=None,
        fm_err=None,
        has_fm=False,
    )
    # Act
    insecure = collect_insecure_http_links(ctx)
    # Assert
    assert insecure == ["http://example.com"]


def test_collect_broken_links_skips_insecure_http(tmp_path: Path) -> None:
    # Arrange — HTTP targets are handled by collect_insecure_http_links
    plugin_root = tmp_path / "plugin"
    plugin_root.mkdir()
    ctx = AuditContext(
        plugin_root=plugin_root,
        rel_path="skills/foo/SKILL.md",
        rel=Path("skills/foo/SKILL.md"),
        target=plugin_root / "skills/foo/SKILL.md",
        text="",
        artifact_type="skill",
        body="[bad](http://example.com/page)\n",
        fm=None,
        fm_err=None,
        has_fm=False,
    )
    # Act
    broken = collect_broken_links(ctx)
    # Assert
    assert broken == []
