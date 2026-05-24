"""Shared fixtures for audit_static tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

PLUGIN_TEST_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PLUGIN_TEST_ROOT.parents[1]
PLUGIN_NAME = PLUGIN_TEST_ROOT.name
PLUGIN_ROOT = REPO_ROOT / "plugins" / PLUGIN_NAME
FIXTURES_DIR = PLUGIN_TEST_ROOT / "fixtures"
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
import audit_static  # noqa: E402


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def plugin_root() -> Path:
    return PLUGIN_ROOT


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def audit():
    """Loaded audit_static module."""
    return audit_static


@pytest.fixture
def mini_plugin(tmp_path: Path, fixtures_dir: Path):
    """Copy a fixture subtree to a temp plugin root."""

    def _copy(case_name: str) -> Path:
        src = fixtures_dir / case_name
        if not src.is_dir():
            raise FileNotFoundError(src)
        dest = tmp_path / case_name
        shutil.copytree(src, dest)
        return dest

    return _copy


def result_by_id(results: list[dict], check_id: str) -> dict:
    for row in results:
        if row["id"] == check_id:
            return row
    raise KeyError(check_id)


def all_pass(results: list[dict]) -> bool:
    return all(r["result"] == "PASS" for r in results)
