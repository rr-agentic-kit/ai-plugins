"""Unit tests for headings_present and resolve_link."""

from __future__ import annotations

from pathlib import Path

import audit_static as m


def test_headings_present_trims_whitespace():
    body = "##  Purpose \n\n## When to use\n"
    assert m.headings_present(body) == {"Purpose", "When to use"}


def test_resolve_link_skips_external_and_anchor(plugin_root: Path):
    source = plugin_root / "README.md"
    assert m.resolve_link(plugin_root, source, "https://example.com")
    assert m.resolve_link(plugin_root, source, "#section")
    assert m.resolve_link(plugin_root, source, "mailto:a@b.c")


def test_resolve_link_valid_relative(mini_plugin):
    root = mini_plugin("skill_valid_link")
    source = root / "skills/my-skill/SKILL.md"
    assert m.resolve_link(root, source, "sibling.md")


def test_resolve_link_broken(plugin_root: Path):
    source = plugin_root / "README.md"
    assert not m.resolve_link(plugin_root, source, "no-such-file.md")


def test_resolve_link_outside_plugin(plugin_root: Path, tmp_path: Path):
    outside = tmp_path / "outside.md"
    outside.write_text("x", encoding="utf-8")
    source = plugin_root / "README.md"
    assert not m.resolve_link(plugin_root, source, str(outside))
