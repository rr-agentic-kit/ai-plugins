from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from audit_static.detect import detect_type
from audit_static.orchestrator import run_checks
from audit_static.report import format_markdown

_DEFAULT_SKILL_GLOB = "skills/*/SKILL.md"


def _resolve_relative_path(plugin_root: Path, rel_path: str) -> str:
    rel = rel_path.lstrip("/")
    if rel not in ("", "."):
        return rel

    plugin_root = plugin_root.resolve()
    skills = sorted(plugin_root.glob(_DEFAULT_SKILL_GLOB))
    if len(skills) == 1:
        return skills[0].relative_to(plugin_root).as_posix()
    if not skills:
        raise SystemExit(
            f"no {_DEFAULT_SKILL_GLOB} under {plugin_root}; "
            "pass a plugin-relative file path"
        )
    paths = ", ".join(p.relative_to(plugin_root).as_posix() for p in skills)
    raise SystemExit(
        f"relative_path '.' is ambiguous ({len(skills)} skills); pass one of: {paths}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Static audit for plugin artifacts",
        epilog=(
            "Examples:\n"
            "  From plugin root:\n"
            "    python3 scripts/audit_static.py . skills/context-engineer/SKILL.md\n"
            "  From monorepo root (audit default skill when only one exists):\n"
            "    python3 plugins/context-eng-hero/scripts/audit_static.py "
            "plugins/context-eng-hero .\n"
            "  From monorepo root (explicit artifact):\n"
            "    python3 plugins/context-eng-hero/scripts/audit_static.py "
            "plugins/context-eng-hero skills/context-engineer/SKILL.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("plugin_root", type=Path, help="Plugin root directory")
    parser.add_argument(
        "relative_path",
        help=(
            "Artifact path relative to plugin root, or '.' "
            "for the sole skills/*/SKILL.md"
        ),
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format",
    )
    args = parser.parse_args()
    rel = _resolve_relative_path(args.plugin_root, args.relative_path)
    results = run_checks(args.plugin_root, rel)
    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        artifact_type = detect_type(Path(rel))
        print(format_markdown(results, rel, artifact_type))
    return 0 if all(r["result"] == "PASS" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
