from __future__ import annotations

from audit_static.models import CheckResult


def check(
    check_id: str,
    severity: str,
    passed: bool,
    evidence: str,
) -> CheckResult:
    return {
        "id": check_id,
        "severity": severity,
        "result": "PASS" if passed else "FAIL",
        "evidence": evidence,
    }


def severity_summary(results: list[CheckResult]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for r in results:
        sev = r["severity"]
        summary.setdefault(sev, {"pass": 0, "total": 0})
        summary[sev]["total"] += 1
        if r["result"] == "PASS":
            summary[sev]["pass"] += 1
    return summary


def format_markdown(
    results: list[CheckResult],
    rel_path: str,
    artifact_type: str,
) -> str:
    lines = [
        f"# Static checks: {artifact_type} — {rel_path}",
        "",
        "## Severity summary",
    ]
    for sev in ("critical", "major", "minor"):
        s = severity_summary(results).get(sev, {"pass": 0, "total": 0})
        lines.append(f"- {sev.capitalize()}: {s['pass']}/{s['total']}")
    lines.extend(
        [
            "",
            "## Static checks",
            "",
            "| id | Severity | PASS/FAIL | Evidence |",
            "|----|----------|-----------|----------|",
        ]
    )
    for r in results:
        lines.append(
            f"| {r['id']} | {r['severity']} | {r['result']} | {r['evidence']} |"
        )
    return "\n".join(lines) + "\n"
