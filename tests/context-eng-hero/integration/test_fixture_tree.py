"""Integration: CLI exit matches all_pass for explicit fixture targets."""

from __future__ import annotations

import subprocess
import sys

import audit_static as m
import pytest

from conftest import FIXTURE_CASES, all_pass


@pytest.mark.parametrize(
    ("case_dir", "rel_path", "_expect_pass"),
    FIXTURE_CASES,
    ids=[f"{c}-{p}" for c, p, _ in FIXTURE_CASES],
)
def test_each_fixture_case_runs(
    case_dir: str, rel_path: str, _expect_pass: bool, mini_plugin, plugin_root
):
    root = mini_plugin(case_dir)
    results = m.run_checks(root, rel_path)
    assert results, "expected at least one check row"
    script = plugin_root / "scripts" / "audit_static.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(root), rel_path],
        capture_output=True,
        text=True,
        check=False,
    )
    expected_code = 0 if all_pass(results) else 1
    assert proc.returncode == expected_code, proc.stdout + proc.stderr
