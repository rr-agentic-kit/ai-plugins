#!/usr/bin/env python3.14
"""CLI entry and backward-compatible import shim for audit_static package."""

from __future__ import annotations

import sys

from audit_static import (
    check,
    detect_type,
    format_markdown,
    headings_present,
    main,
    parse_frontmatter,
    resolve_link,
    run_checks,
    severity_summary,
)

__all__ = [
    "check",
    "detect_type",
    "format_markdown",
    "headings_present",
    "main",
    "parse_frontmatter",
    "resolve_link",
    "run_checks",
    "severity_summary",
]

if __name__ == "__main__":
    sys.exit(main())
