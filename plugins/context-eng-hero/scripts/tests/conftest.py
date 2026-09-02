"""Shared fixtures for context-eng-hero script tests."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = SCRIPTS_DIR.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def load_module(module_name: str, relative_path: str):
    """Load a module from a file under SCRIPTS_DIR (atlassia-style helper)."""
    path = SCRIPTS_DIR / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def import_audit_static():
    """Import the audit_static package from SCRIPTS_DIR."""
    return importlib.import_module("audit_static")
