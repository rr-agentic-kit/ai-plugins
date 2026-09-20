"""Unit tests for parse_frontmatter."""

from __future__ import annotations

import audit_static as m
import pytest


@pytest.mark.parametrize(
    ("text", "expect_fm", "body_substr"),
    [
        (
            "---\nname: a\ndescription: b\n---\n\n# Body\n",
            {"name": "a", "description": "b"},
            "# Body",
        ),
        ("---\n---\n\n# Body\n", {}, "# Body"),
    ],
    ids=["valid_yaml", "empty_block"],
)
def test_frontmatter_happy(text: str, expect_fm: dict, body_substr: str):
    fm, body, err = m.parse_frontmatter(text)
    assert err is None
    assert fm == expect_fm
    assert body_substr in body


@pytest.mark.parametrize(
    ("text", "err_substr", "expect_body"),
    [
        ("name: x\n\n# Body", "missing opening --- delimiter", "name: x\n\n# Body"),
        ("---\nname: a\n", "missing closing --- delimiter", None),
        ("---\nname: [\n---\n\n# Body\n", "YAML parse error", None),
        ("---\n- list\n---\n\n# Body\n", "frontmatter must be a YAML mapping", None),
    ],
    ids=["no_open", "no_close", "bad_yaml", "non_mapping"],
)
def test_frontmatter_errors(text: str, err_substr: str, expect_body: str | None):
    fm, body, err = m.parse_frontmatter(text)
    assert fm is None
    assert err is not None
    assert err_substr in err
    if expect_body is not None:
        assert body == expect_body


def test_no_pyyaml(monkeypatch):
    monkeypatch.setattr(m, "yaml", None)
    text = "---\nname: a\n---\n\n# Body\n"
    fm, _, err = m.parse_frontmatter(text)
    assert fm is None
    assert "pyyaml not installed" in (err or "")
