"""Tests for render_ce_report.py — main() units + thin subprocess smokes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import render_ce_report as r

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "context-eng-hero"
    / "scripts"
    / "render_ce_report.py"
)

_COMPLIANCE: dict[str, Any] = {
    "status": "ok",
    "kind": "compliance",
    "target": {"path": "skills/x/SKILL.md", "type": "Skill+Ref", "title": "x"},
    "summary": {"verdict": "FAIL", "static": "PASS", "top_patterns": "FORMAT"},
    "severity": {
        "critical": {"pass": 2, "total": 2},
        "major": {"pass": 1, "total": 1},
        "minor": {"pass": 0, "total": 1},
    },
    "checks": [
        {
            "id": "skill-ref.readme.philosophy",
            "severity": "minor",
            "result": "FAIL",
            "evidence": "7 bullets",
        }
    ],
    "findings_narrative": "trim philosophy",
}

_APPLY_PLAN: dict[str, Any] = {
    "kind": "apply-plan",
    "reports": {
        "compliance": "a/compliance.md",
        "opportunity": "a/opportunity.md",
        "apply_plan": "a/apply-plan.md",
    },
    "fix": [],
    "redesign": [],
}

_OPPORTUNITY: dict[str, Any] = {
    "kind": "opportunity",
    "target": {"path": "skills/x/SKILL.md", "type": "Skill+Ref", "title": "x"},
    "compliance_blockers": "none",
    "keep": ["stable Purpose"],
    "challenge": "FN walked SCRIPTABLE.",
    "ranked": [
        {
            "rank": 1,
            "id": "imp.load.report-scaffold",
            "pattern": "SCRIPTABLE",
            "stance": "Improve",
            "impact": "high",
            "confidence": "observed",
            "absorb": "fix",
            "summary": "paste full markdown every turn",
        }
    ],
    "opportunity_detail": "lean JSON + render",
    "deferred": [],
}

_REFLECTION: dict[str, Any] = {
    "kind": "reflection",
    "target": "skills/x/SKILL.md",
    "type": "Skill+Ref",
    "result": "PASSED",
    "deep_reflect": ["signal clear", "no scaffold paste"],
    "harness_summary": {
        "reliable": "yes",
        "consistent": "yes",
        "deterministic": "yes",
    },
    "judgment": [
        {
            "id": "reflect.judgment.ok",
            "severity": "major",
            "result": "PASS",
            "evidence": "draft matches intent",
        }
    ],
    "harness": [
        {
            "id": "reflect.harness.ok",
            "severity": "minor",
            "result": "PASS",
            "evidence": "static reused",
        }
    ],
    "top_patterns": "(none)",
}


def _run_main(
    kind: str,
    payload: dict[str, Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    infile: str | None = None,
) -> tuple[int, str, str]:
    src = tmp_path / f"{kind}.json"
    out = tmp_path / f"{kind}.md"
    src.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    argv = ["render_ce_report.py", kind, "--out", out.name]
    if infile == "-":
        argv.extend(["--in", "-"])
        monkeypatch.setattr(sys, "stdin", src.open(encoding="utf-8"))
    else:
        argv.extend(["--in", src.name])
    monkeypatch.setattr(sys, "argv", argv)
    from io import StringIO

    out_buf, err_buf = StringIO(), StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)
    try:
        code = r.main()
    except SystemExit as exc:
        code = int(exc.code) if isinstance(exc.code, int) else 1
    return code, out_buf.getvalue(), err_buf.getvalue()


@pytest.mark.parametrize(
    ("kind", "payload", "must_contain"),
    [
        (
            "compliance",
            _COMPLIANCE,
            ("Critical: 2/2", "skill-ref.readme.philosophy", "Verdict: FAIL"),
        ),
        ("apply-plan", _APPLY_PLAN, ("(empty)",)),
        (
            "opportunity",
            _OPPORTUNITY,
            ("imp.load.report-scaffold", "SCRIPTABLE", "stable Purpose"),
        ),
        (
            "reflection",
            _REFLECTION,
            (
                "Result: **PASSED**",
                "reflect.judgment.ok",
                "PASSED: proceed to pre-ship",
            ),
        ),
    ],
    ids=["compliance", "apply-plan", "opportunity", "reflection"],
)
def test_render_main_happy(
    kind: str,
    payload: dict[str, Any],
    must_contain: tuple[str, ...],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    code, stdout, stderr = _run_main(kind, payload, tmp_path, monkeypatch)
    assert code == 0, stderr
    assert "wrote" in stdout
    text = (tmp_path / f"{kind}.md").read_text(encoding="utf-8")
    for needle in must_contain:
        assert needle in text


def test_render_main_stdin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    code, stdout, stderr = _run_main(
        "compliance", _COMPLIANCE, tmp_path, monkeypatch, infile="-"
    )
    assert code == 0, stderr
    assert "wrote" in stdout


def test_render_main_schema_miss(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    empty = tmp_path / "empty_reports"
    empty.mkdir()
    monkeypatch.setattr(r, "_reports_dir", lambda _root: empty)
    code, _stdout, stderr = _run_main("compliance", _COMPLIANCE, tmp_path, monkeypatch)
    assert code == 2
    assert "missing schema" in stderr or "render_ce_report error" in stderr


def test_render_main_invalid_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {
        "kind": "compliance",
        "target": {"path": "skills/x/SKILL.md", "type": "Skill"},
    }
    code, _stdout, stderr = _run_main("compliance", payload, tmp_path, monkeypatch)
    assert code == 2
    assert "validation error" in stderr


def test_render_subprocess_smoke(tmp_path: Path) -> None:
    """Keep one entry-script smoke for the __main__ shim."""
    src = tmp_path / "compliance.json"
    out = tmp_path / "compliance.md"
    src.write_text(json.dumps(_COMPLIANCE), encoding="utf-8")
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "compliance",
            "--in",
            src.name,
            "--out",
            out.name,
        ],
        check=False,
        capture_output=True,
        cwd=tmp_path,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "wrote" in proc.stdout
    assert "Critical: 2/2" in out.read_text(encoding="utf-8")


def test_render_rejects_path_outside_cwd(tmp_path: Path) -> None:
    outside = tmp_path.parent / "escape-payload.json"
    outside.write_text("{}", encoding="utf-8")
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "compliance",
            "--in",
            str(outside),
            "--out",
            "out.md",
        ],
        check=False,
        capture_output=True,
        cwd=tmp_path,
        text=True,
    )
    assert proc.returncode == 2
    assert "outside the allowed directory" in proc.stderr
