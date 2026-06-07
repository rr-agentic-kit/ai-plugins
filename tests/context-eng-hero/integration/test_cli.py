"""CLI integration tests via subprocess."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run_cli(
    plugin_root: Path,
    rel_path: str,
    *,
    script: Path,
    repo_root: Path,
    fmt: str = "markdown",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(script),
            str(plugin_root),
            rel_path,
            "--format",
            fmt,
        ],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        check=False,
    )


def test_cli_skill_passes(plugin_root, repo_root):
    script = plugin_root / "scripts" / "audit_static.py"
    proc = run_cli(
        plugin_root,
        "skills/recipe-context-engineer/SKILL.md",
        script=script,
        repo_root=repo_root,
    )
    assert proc.returncode == 0
    assert "## Static checks" in proc.stdout


def test_cli_skill_fails_on_fixture(mini_plugin, plugin_root, repo_root):
    root = mini_plugin("skill_bad_name")
    script = plugin_root / "scripts" / "audit_static.py"
    proc = run_cli(
        root,
        "skills/my-skill/SKILL.md",
        script=script,
        repo_root=repo_root,
    )
    assert proc.returncode == 1


def test_cli_json_format(plugin_root, repo_root):
    script = plugin_root / "scripts" / "audit_static.py"
    proc = run_cli(
        plugin_root,
        "skills/recipe-context-engineer/SKILL.md",
        script=script,
        repo_root=repo_root,
        fmt="json",
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert isinstance(data, list)
    for row in data:
        assert set(row.keys()) >= {"id", "severity", "result", "evidence"}


def test_cli_dot_relative_ambiguous_when_multiple_skills(plugin_root, repo_root):
    """'.' under plugin_root lists skills when multiple skills/*/SKILL.md exist."""
    script = plugin_root / "scripts" / "audit_static.py"
    proc = run_cli(
        plugin_root,
        ".",
        script=script,
        repo_root=repo_root,
    )
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "ambiguous" in proc.stderr
    assert "skills/recipe-context-engineer/SKILL.md" in proc.stderr
    assert "skills/recipe-static-memory/SKILL.md" in proc.stderr


def test_cli_markdown_severity_summary(plugin_root, repo_root):
    script = plugin_root / "scripts" / "audit_static.py"
    proc = run_cli(
        plugin_root,
        "skills/recipe-context-engineer/SKILL.md",
        script=script,
        repo_root=repo_root,
    )
    assert "Severity summary" in proc.stdout or "## Severity summary" in proc.stdout
