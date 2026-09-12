"""Unit tests for lexicon companion presence/shape checks."""

from __future__ import annotations

from pathlib import Path

import audit_static as m
from audit_static.models import AuditContext
from audit_static.runners.lexicon import run_lexicon
from conftest import result_by_id


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _ctx(root: Path, rel: str) -> AuditContext:
    loaded = AuditContext.load(root, rel)
    assert isinstance(loaded, AuditContext)
    return loaded


def _results_map(results: list[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in results}


EMPTY_ACRONYMS = """# Acronyms

| Acronym | Expansion | Notes |
|---------|-----------|-------|
"""

EMPTY_GLOSSARY = """# Glossary

| Term | Meaning (this plugin) | Not confused with | Notes |
|------|----------------------|-------------------|-------|
"""

NONE_YET_ACRONYMS = """# Acronyms

| Acronym | Expansion | Notes |
|---------|-----------|-------|
| None yet | — | — |
"""

NONE_YET_GLOSSARY = """# Glossary

| Term | Meaning (this plugin) | Not confused with | Notes |
|------|----------------------|-------------------|-------|
| None yet | — | — | — |
"""


def test_detect_acronyms_and_glossary():
    assert m.detect_type(Path("ACRONYMS.md")) == "acronyms"
    assert m.detect_type(Path("GLOSSARY.md")) == "glossary"
    assert m.detect_type(Path("skills/x/ACRONYMS.md")) == "acronyms"


def test_presence_fail_when_companions_missing(tmp_path: Path):
    _write(
        tmp_path,
        "skills/x/SKILL.md",
        "---\nname: x\ndescription: d\n---\n\n## Purpose\n\n## When to use\n\n## Procedure\n",
    )
    ctx = _ctx(tmp_path, "skills/x/SKILL.md")
    results = _results_map(run_lexicon(ctx))
    assert results["static.acronyms.present"]["result"] == "FAIL"
    assert results["static.glossary.present"]["result"] == "FAIL"


def test_presence_pass_when_companions_exist(tmp_path: Path):
    _write(tmp_path, "ACRONYMS.md", EMPTY_ACRONYMS)
    _write(tmp_path, "GLOSSARY.md", EMPTY_GLOSSARY)
    _write(
        tmp_path,
        "skills/x/SKILL.md",
        "---\nname: x\ndescription: d\n---\n\n## Purpose\n\n## When to use\n\n## Procedure\n",
    )
    ctx = _ctx(tmp_path, "skills/x/SKILL.md")
    results = _results_map(run_lexicon(ctx))
    assert results["static.acronyms.present"]["result"] == "PASS"
    assert results["static.glossary.present"]["result"] == "PASS"


def test_acronyms_empty_table_shape_pass(tmp_path: Path):
    _write(tmp_path, "ACRONYMS.md", EMPTY_ACRONYMS)
    _write(tmp_path, "GLOSSARY.md", EMPTY_GLOSSARY)
    ctx = _ctx(tmp_path, "ACRONYMS.md")
    results = _results_map(run_lexicon(ctx))
    assert results["static.acronyms.present"]["result"] == "PASS"
    assert results["static.acronyms.shape"]["result"] == "PASS"


def test_glossary_none_yet_shape_pass(tmp_path: Path):
    _write(tmp_path, "ACRONYMS.md", NONE_YET_ACRONYMS)
    _write(tmp_path, "GLOSSARY.md", NONE_YET_GLOSSARY)
    ctx = _ctx(tmp_path, "GLOSSARY.md")
    results = _results_map(run_lexicon(ctx))
    assert results["static.glossary.present"]["result"] == "PASS"
    assert results["static.glossary.shape"]["result"] == "PASS"


def test_acronyms_shape_fail_missing_columns(tmp_path: Path):
    _write(tmp_path, "ACRONYMS.md", "# Acronyms\n\nNo table here.\n")
    _write(tmp_path, "GLOSSARY.md", EMPTY_GLOSSARY)
    ctx = _ctx(tmp_path, "ACRONYMS.md")
    row = result_by_id(run_lexicon(ctx), "static.acronyms.shape")
    assert row["result"] == "FAIL"


def test_glossary_shape_fail_missing_h1(tmp_path: Path):
    _write(
        tmp_path,
        "GLOSSARY.md",
        "| Term | Meaning (this plugin) | Not confused with | Notes |\n"
        "|------|----------------------|-------------------|-------|\n",
    )
    _write(tmp_path, "ACRONYMS.md", EMPTY_ACRONYMS)
    ctx = _ctx(tmp_path, "GLOSSARY.md")
    row = result_by_id(run_lexicon(ctx), "static.glossary.shape")
    assert row["result"] == "FAIL"


def test_run_checks_acronyms_file(tmp_path: Path):
    _write(tmp_path, "ACRONYMS.md", NONE_YET_ACRONYMS)
    _write(tmp_path, "GLOSSARY.md", NONE_YET_GLOSSARY)
    results = m.run_checks(tmp_path, "ACRONYMS.md")
    by_id = _results_map(results)
    assert by_id["static.acronyms.present"]["result"] == "PASS"
    assert by_id["static.acronyms.shape"]["result"] == "PASS"
    assert by_id["static.glossary.present"]["result"] == "PASS"
