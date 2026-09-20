"""Smoke tests for render_ce_report.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "context-eng-hero"
    / "scripts"
    / "render_ce_report.py"
)


def _run(kind: str, payload: dict, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    src = tmp_path / f"{kind}.json"
    out = tmp_path / f"{kind}.md"
    src.write_text(json.dumps(payload), encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            kind,
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


def test_render_compliance_severity_math(tmp_path: Path) -> None:
    payload = {
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
    proc = _run("compliance", payload, tmp_path)
    assert proc.returncode == 0, proc.stderr
    text = (tmp_path / "compliance.md").read_text(encoding="utf-8")
    assert "Critical: 2/2" in text
    assert "Minor: 0/1" in text
    assert "skill-ref.readme.philosophy" in text
    assert "Verdict: FAIL" in text


def test_render_apply_plan_empty_lanes(tmp_path: Path) -> None:
    payload = {
        "kind": "apply-plan",
        "reports": {
            "compliance": "a/compliance.md",
            "opportunity": "a/opportunity.md",
            "apply_plan": "a/apply-plan.md",
        },
        "fix": [],
        "redesign": [],
    }
    proc = _run("apply-plan", payload, tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "(empty)" in (tmp_path / "apply-plan.md").read_text(encoding="utf-8")


def test_render_opportunity_happy_path(tmp_path: Path) -> None:
    payload = {
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
    proc = _run("opportunity", payload, tmp_path)
    assert proc.returncode == 0, proc.stderr
    text = (tmp_path / "opportunity.md").read_text(encoding="utf-8")
    assert "Audit-redesign: Skill+Ref — x" in text
    assert "imp.load.report-scaffold" in text
    assert "SCRIPTABLE" in text
    assert "stable Purpose" in text


def test_render_reflection_happy_path(tmp_path: Path) -> None:
    payload = {
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
    proc = _run("reflection", payload, tmp_path)
    assert proc.returncode == 0, proc.stderr
    text = (tmp_path / "reflection.md").read_text(encoding="utf-8")
    assert "Result: **PASSED**" in text
    assert "reflect.judgment.ok" in text
    assert "PASSED: proceed to pre-ship" in text


def test_render_invalid_payload_exit_2(tmp_path: Path) -> None:
    # Missing required summary / severity / checks for compliance.
    payload = {
        "kind": "compliance",
        "target": {"path": "skills/x/SKILL.md", "type": "Skill"},
    }
    proc = _run("compliance", payload, tmp_path)
    assert proc.returncode == 2
    err = proc.stderr
    assert "validation error" in err
    assert "required" in err.lower() or "summary" in err


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
