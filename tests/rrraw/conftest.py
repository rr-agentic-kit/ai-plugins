"""Shared fixtures for rrraw validate_planning tests."""

from __future__ import annotations

import sys
from pathlib import Path

PLUGIN_TEST_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = PLUGIN_TEST_ROOT.parents[1] / "plugins" / PLUGIN_TEST_ROOT.name / "scripts"

sys.path.insert(0, str(PLUGIN_TEST_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))
import validate_planning as vp  # noqa: E402, F401
