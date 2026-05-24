"""Unit tests for parse_frontmatter."""

from __future__ import annotations

import audit_static as m


def test_valid_yaml():
    text = "---\nname: a\ndescription: b\n---\n\n# Body\n"
    fm, body, err = m.parse_frontmatter(text)
    assert err is None
    assert fm == {"name": "a", "description": "b"}
    assert body.startswith("# Body")


def test_missing_opening_delimiter():
    fm, body, err = m.parse_frontmatter("name: x\n\n# Body")
    assert fm is None
    assert err == "missing opening --- delimiter"
    assert body == "name: x\n\n# Body"


def test_missing_closing_delimiter():
    text = "---\nname: a\n"
    fm, _, err = m.parse_frontmatter(text)
    assert fm is None
    assert err == "missing closing --- delimiter"


def test_invalid_yaml():
    text = "---\nname: [\n---\n\n# Body\n"
    fm, _, err = m.parse_frontmatter(text)
    assert fm is None
    assert err is not None
    assert "YAML parse error" in err


def test_non_mapping_root():
    text = "---\n- list\n---\n\n# Body\n"
    fm, _, err = m.parse_frontmatter(text)
    assert fm is None
    assert err == "frontmatter must be a YAML mapping"


def test_empty_frontmatter_block():
    text = "---\n---\n\n# Body\n"
    fm, body, err = m.parse_frontmatter(text)
    assert err is None
    assert fm == {}
    assert "# Body" in body


def test_no_pyyaml(monkeypatch):
    monkeypatch.setattr(m, "yaml", None)
    text = "---\nname: a\n---\n\n# Body\n"
    fm, _, err = m.parse_frontmatter(text)
    assert fm is None
    assert "pyyaml not installed" in (err or "")
