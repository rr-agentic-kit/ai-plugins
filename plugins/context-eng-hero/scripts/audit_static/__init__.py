"""Static audit checks for context-eng-hero plugin artifacts."""

from __future__ import annotations

from audit_static import frontmatter as _frontmatter
from audit_static.cli import main
from audit_static.detect import detect_type
from audit_static.frontmatter import parse_frontmatter
from audit_static.headings import headings_present
from audit_static.links import resolve_link
from audit_static.orchestrator import run_checks
from audit_static.report import check, format_markdown, severity_summary

yaml = _frontmatter.yaml

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
    "yaml",
]
