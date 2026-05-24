"""Integration: each fixture case behaves as expected end-to-end."""

from __future__ import annotations

import subprocess
import sys

import audit_static as m
import pytest
from conftest import FIXTURES_DIR, all_pass


@pytest.mark.parametrize(
    "case_dir",
    [p.name for p in FIXTURES_DIR.iterdir() if p.is_dir()],
)
def test_each_fixture_case_runs(case_dir: str, mini_plugin, plugin_root):
    root = mini_plugin(case_dir)
    md_files = list(root.rglob("*.md")) + list(root.rglob("*.mdc"))
    assert md_files, f"no artifacts in {case_dir}"
    target = md_files[0].relative_to(root).as_posix()
    results = m.run_checks(root, target)
    assert results, "expected at least one check row"
    script = plugin_root / "scripts" / "audit_static.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(root), target],
        capture_output=True,
        text=True,
        check=False,
    )
    expected_code = 0 if all_pass(results) else 1
    assert proc.returncode == expected_code, proc.stdout + proc.stderr
