from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from audit_static.detect import detect_type
from audit_static.orchestrator import run_checks
from audit_static.report import format_markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Static audit for plugin artifacts")
    parser.add_argument("plugin_root", type=Path, help="Plugin root directory")
    parser.add_argument("relative_path", help="Path relative to plugin root")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format",
    )
    args = parser.parse_args()
    rel = args.relative_path.lstrip("/")
    results = run_checks(args.plugin_root, rel)
    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        artifact_type = detect_type(Path(rel))
        print(format_markdown(results, rel, artifact_type))
    return 0 if all(r["result"] == "PASS" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
