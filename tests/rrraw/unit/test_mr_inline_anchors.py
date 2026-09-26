"""Unit tests for rr-ci mr-inline-anchors diff parse."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "rrraw"
    / "skills"
    / "s-ci"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import mr_inline_anchors  # noqa: E402

FIXTURE_DIFF = """\
diff --git a/src/a.py b/src/a.py
--- a/src/a.py
+++ b/src/a.py
@@ -1,4 +1,6 @@
 def hello():
-    return 1
+    # note
+    return 2
+
     pass
@@ -10,3 +12,4 @@
     x = 1
+    y = 2
     z = 3
"""


def test_parse_unified_diff_plus_lines() -> None:
    assert mr_inline_anchors.parse_unified_diff_plus_lines(FIXTURE_DIFF) == [
        2,
        3,
        4,
        13,
    ]


def test_parse_ignores_file_headers_and_deletions() -> None:
    diff = """\
--- a/x
+++ b/x
@@ -1,3 +1,2 @@
 keep
-gone
 still
"""
    assert mr_inline_anchors.parse_unified_diff_plus_lines(diff) == []


def test_parse_empty() -> None:
    assert mr_inline_anchors.parse_unified_diff_plus_lines("") == []
