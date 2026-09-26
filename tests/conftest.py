"""Repo-wide test setup."""

from __future__ import annotations

import os

import pytest

# Tests across this suite build throwaway git repos under tmp_path and target
# them via `cwd=` (or monkeypatch.chdir), relying on git's normal cwd-based
# repo discovery. git prefers these env vars over cwd when they're set, so if
# the pytest process itself inherits them from an ambient git hook (e.g. this
# repo's own lefthook pre-commit `pytest` step), every "isolated" fixture git
# call — and every git call made by source code under test — silently
# operates on the real enclosing repository instead of the fixture.
_AMBIENT_GIT_ENV = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_COMMON_DIR",
    "GIT_CEILING_DIRECTORIES",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_PREFIX",
)


@pytest.fixture(autouse=True, scope="session")
def _strip_ambient_git_env() -> None:
    for name in _AMBIENT_GIT_ENV:
        os.environ.pop(name, None)
