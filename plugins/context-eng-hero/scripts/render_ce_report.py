#!/usr/bin/env python3
"""Render CE improve reports from lean JSON + on-disk Jinja templates.

Agent emits small JSON; this script validates against JSON Schema, then renders
markdown. Does not invent audit findings — only formats caller-supplied rows.

Usage (from context-eng-hero plugin root or monorepo with paths):

  python3 scripts/render_ce_report.py compliance --in payload.json --out compliance.md
  python3 scripts/render_ce_report.py opportunity --in payload.json --out opportunity.md
  python3 scripts/render_ce_report.py apply-plan --in payload.json --out apply-plan.md
  python3 scripts/render_ce_report.py reflection --in in.json --out out.md

Stdout: one line `wrote <path>` on success. Exit 0 on success; exit 2 on
validation / I/O / JSON errors (stderr paths for the LLM to fix).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateError, select_autoescape
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

_KINDS = ("compliance", "opportunity", "apply-plan", "reflection")

# CLI kind → on-disk stem (same for schema + template today).
_KIND_STEM: dict[str, str] = {k: k for k in _KINDS}


def _plugin_root() -> Path:
    """scripts/render_ce_report.py → plugin root."""
    return Path(__file__).resolve().parent.parent


def _reports_dir(plugin_root: Path) -> Path:
    return (
        plugin_root
        / "skills"
        / "recipe-context-engineer"
        / "refs"
        / "templates"
        / "reports"
    )


def _safe_cli_path(path: Path) -> Path:
    """Canonicalize CLI paths and confine them to the process cwd (S8707)."""
    resolved = Path(os.path.realpath(path))
    base = Path(os.path.realpath(os.getcwd()))
    if resolved != base and not resolved.is_relative_to(base):
        raise ValueError(f"path {str(path)!r} is outside the allowed directory")
    return resolved


def _load(path: Path | None) -> dict[str, Any]:
    if path is None or str(path) == "-":
        raw = sys.stdin.read()
    else:
        raw = _safe_cli_path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("payload must be a JSON object")
    return data


def _json_path(error: ValidationError) -> str:
    parts = [str(p) for p in error.absolute_path]
    return "$" if not parts else "$." + ".".join(parts)


def _print_validation_errors(errors: list[ValidationError]) -> None:
    print("render_ce_report validation error:", file=sys.stderr)
    # Stable order: deeper paths first, then message.
    for err in sorted(errors, key=lambda e: (list(e.absolute_path), e.message)):
        print(f"{_json_path(err)}: {err.message}", file=sys.stderr)


def _validate(data: dict[str, Any], schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if errors:
        _print_validation_errors(errors)
        raise SystemExit(2)


def _render(kind: str, data: dict[str, Any], reports_dir: Path) -> str:
    stem = _KIND_STEM[kind]
    env = Environment(
        loader=FileSystemLoader(str(reports_dir)),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    template = env.get_template(f"{stem}.md.j2")
    return template.render(**data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "kind",
        choices=sorted(_KINDS),
        help="Report kind to render",
    )
    parser.add_argument(
        "--in",
        dest="infile",
        type=Path,
        default=None,
        help="JSON payload path (default: stdin; use - for stdin)",
    )
    parser.add_argument(
        "--out",
        dest="outfile",
        type=Path,
        required=True,
        help="Markdown output path",
    )
    args = parser.parse_args()
    reports_dir = _reports_dir(_plugin_root())
    stem = _KIND_STEM[args.kind]
    schema_path = reports_dir / f"{stem}.schema.json"
    try:
        if not schema_path.is_file():
            raise FileNotFoundError(f"missing schema: {schema_path}")
        data = _load(args.infile)
        _validate(data, schema_path)
        body = _render(args.kind, data, reports_dir)
        outfile = _safe_cli_path(args.outfile)
        outfile.parent.mkdir(parents=True, exist_ok=True)
        outfile.write_text(body.rstrip() + "\n", encoding="utf-8")
    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        TemplateError,
    ) as exc:
        print(f"render_ce_report error: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {outfile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
