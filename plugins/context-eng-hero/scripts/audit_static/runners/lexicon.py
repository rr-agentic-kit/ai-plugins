from __future__ import annotations

import re

from audit_static.models import AuditContext, CheckResult
from audit_static.report import check

_H1_RE = re.compile(r"^#\s+\S", re.MULTILINE)

_SHIPPABLE_TYPES = frozenset(
    {
        "skill",
        "skill-readme",
        "command",
        "agent",
        "rule",
        "workflow",
        "ref-file",
        "acronyms",
        "glossary",
    }
)

_ACRONYMS_COLS = ("Acronym", "Expansion")
_GLOSSARY_COLS = ("Term", "Meaning")


def _table_has_columns(text: str, required: tuple[str, ...]) -> bool:
    required_lower = tuple(c.lower() for c in required)
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("|--"):
            continue
        cells = [c.strip().lower() for c in stripped.strip("|").split("|")]
        if all(any(req in cell for cell in cells) for req in required_lower):
            return True
    return False


def _shape_ok(text: str, required_cols: tuple[str, ...]) -> tuple[bool, str]:
    has_h1 = _H1_RE.search(text) is not None
    has_table = _table_has_columns(text, required_cols)
    if has_h1 and has_table:
        return True, "H1 + required table columns present"
    missing: list[str] = []
    if not has_h1:
        missing.append("H1")
    if not has_table:
        missing.append(f"table columns {', '.join(required_cols)}")
    return False, f"missing: {'; '.join(missing)}"


def _presence(plugin_root, filename: str, check_id: str) -> CheckResult:
    path = plugin_root / filename
    exists = path.is_file()
    return check(
        check_id,
        "major",
        exists,
        f"{filename} present" if exists else f"{filename} missing at plugin root",
    )


def run_lexicon(ctx: AuditContext) -> list[CheckResult]:
    results: list[CheckResult] = []

    if ctx.artifact_type in _SHIPPABLE_TYPES:
        results.append(
            _presence(ctx.plugin_root, "ACRONYMS.md", "static.acronyms.present")
        )
        results.append(
            _presence(ctx.plugin_root, "GLOSSARY.md", "static.glossary.present")
        )

    if ctx.artifact_type == "acronyms":
        ok, evidence = _shape_ok(ctx.text, _ACRONYMS_COLS)
        results.append(check("static.acronyms.shape", "major", ok, evidence))
    elif ctx.artifact_type == "glossary":
        ok, evidence = _shape_ok(ctx.text, _GLOSSARY_COLS)
        results.append(check("static.glossary.shape", "major", ok, evidence))

    return results
