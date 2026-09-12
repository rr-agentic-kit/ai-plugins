"""--setup, agent.plan.md, root SoT load line, version-first docs/rr/ layout."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .constants import (
    AGENT_CONFIG_PATH,
    AGENT_PLAN_NAME,
    AGENT_PLAN_TEMPLATE_PATH,
    DISCOVERY_DIR,
    DISCOVERY_STEMS,
    INJECTION_FENCE_RE,
    PLAN_DIR,
    PLAN_STEMS,
    PR_VALIDATE_WORKFLOW_REL,
    PR_VALIDATE_WORKFLOW_TEMPLATE_PATH,
    ROOT_SOT_FILENAMES,
    RRR_STATUS_NAME,
    SETUP_SECTIONS,
    STATUS_NAME,
)
from .layout_migrate import migrate_docs_layout
from .models import Issue, has_errors
from .rewrite import rewrite_planning_dir
from .workspace import (
    compute_mint_hash,
    current_track,
    default_rrr_status,
    default_unfrozen_status,
    ensure_doc_frontmatter,
    fill_rrr_status_missing,
    fill_status_missing,
    find_repo_root,
    find_rrr_status_path,
    find_status_path,
    has_cascade_docs,
    load_status,
    resolve_within_root,
    rr_root,
    rrr_status_path,
    stems_for_dir,
    tasks_dir,
    track_phase_dir,
    write_status_yaml,
)

_MSG_NO_CASCADE_DOCS = "no cascade docs"
_MSG_ALREADY_CANONICAL = "already canonical"


def parse_agent_config(text: str | None = None) -> tuple[int, str, str]:
    raw = text if text is not None else AGENT_CONFIG_PATH.read_text(encoding="utf-8")
    fence = INJECTION_FENCE_RE.search(raw)
    if fence is None:
        raise ValueError("agent-config.md missing injection yaml fence")
    payload = yaml.safe_load(fence.group(1))
    if not isinstance(payload, dict) or "injection" not in payload:
        raise ValueError("agent-config.md injection fence must contain injection:")
    injection = payload["injection"]
    if not isinstance(injection, dict):
        raise ValueError("injection must be a mapping")
    version = injection.get("version")
    load_line = injection.get("load_line")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise ValueError("injection.version must be a positive int")
    if not isinstance(load_line, str) or not load_line.strip():
        raise ValueError("injection.load_line must be a non-empty string")
    try:
        body = AGENT_PLAN_TEMPLATE_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"missing agent.plan.md template: {exc}") from exc
    if not body.strip():
        raise ValueError("agent.plan.md template is empty")
    return version, load_line.strip(), body


def emit_agent_plan(docs: Path, *, body: str | None = None) -> Path:
    """Write ``agent.plan.md`` under ``docs/rr/`` (``docs`` may be docs root or rr)."""
    parking = docs if docs.name == "rr" else rr_root(docs)
    safe_dir = resolve_within_root(parking, find_repo_root(docs))
    safe_dir.mkdir(parents=True, exist_ok=True)
    text = body if body is not None else parse_agent_config()[2]
    path = safe_dir / AGENT_PLAN_NAME
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")
    return path


def sync_root_sot(repo_root: Path, load_line: str | None = None) -> list[Path]:
    line = load_line if load_line is not None else parse_agent_config()[1]
    needle = line.strip()
    updated: list[Path] = []
    for name in sorted(ROOT_SOT_FILENAMES):
        path = repo_root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if needle in text:
            continue
        if text and not text.endswith("\n"):
            text += "\n"
        path.write_text(text + needle + "\n", encoding="utf-8")
        updated.append(path)
    return updated


def sync_agent_injection(
    docs: Path,
    repo_root: Path,
    *,
    force: bool = False,
) -> list[Issue]:
    """Emit docs/rr/agent.plan.md and bump rrr-status claude_config_version."""
    issues: list[Issue] = []
    parking = rr_root(docs) if docs.name != "rr" else docs
    docs_root_path = parking.parent if parking.name == "rr" else docs
    status_path = find_rrr_status_path(docs_root_path)
    plan_path = parking / AGENT_PLAN_NAME
    legacy_plan = docs_root_path / AGENT_PLAN_NAME
    if (
        not force
        and status_path is None
        and not plan_path.is_file()
        and not legacy_plan.is_file()
    ):
        return issues
    try:
        version, load_line, body = parse_agent_config()
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [Issue.error("HAND_BUMP", f"agent-config.md: {exc}")]
    emit_agent_plan(docs_root_path, body=body)
    sync_root_sot(repo_root, load_line)
    if status_path is None:
        return issues
    data, load_issues = load_status(status_path)
    issues.extend(load_issues)
    if data is None:
        return issues
    if data.get("claude_config_version") != version:
        data["claude_config_version"] = version
        write_status_yaml(status_path, data)
    return issues


def setup_mkdir(path: Path, repo_root: Path) -> tuple[str, str]:
    if path.is_file():
        return "failed", f"{path} is a file"
    if path.is_dir():
        return "ok", "exists"
    try:
        resolve_within_root(path, repo_root).mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError) as exc:
        return "failed", str(exc)
    return "created", "mkdir"


def setup_plans_directory(plans_dir: Path, repo_root: Path) -> tuple[str, str]:
    """Legacy alias — prefer :func:`setup_mkdir`."""
    return setup_mkdir(plans_dir, repo_root)


def setup_root_sot(repo_root: Path, load_line: str) -> tuple[str, str]:
    existing = [
        repo_root / name
        for name in sorted(ROOT_SOT_FILENAMES)
        if (repo_root / name).is_file()
    ]
    if not existing:
        return "ok", "no root SoT files"
    updated = sync_root_sot(repo_root, load_line)
    if updated:
        names = ", ".join(path.name for path in updated)
        return "fixed", f"appended load line on {names}"
    return "ok", "already present"


def setup_agent_plan(docs: Path, body: str) -> tuple[str, str]:
    parking = rr_root(docs)
    path = parking / AGENT_PLAN_NAME
    expected = body if body.endswith("\n") else body + "\n"
    if not path.is_file():
        try:
            emit_agent_plan(docs, body=body)
        except OSError as exc:
            return "failed", str(exc)
        return "created", "wrote template"
    current = path.read_text(encoding="utf-8")
    if current == expected:
        return "ok", "matches template"
    try:
        emit_agent_plan(docs, body=body)
    except OSError as exc:
        return "failed", str(exc)
    return "fixed", "overwrote to template"


def setup_rrr_status(docs: Path, injection_version: int) -> tuple[str, str]:
    path = rrr_status_path(docs)
    if not path.is_file():
        legacy = docs / RRR_STATUS_NAME
        if legacy.is_file():
            path = legacy
        else:
            try:
                rr_root(docs).mkdir(parents=True, exist_ok=True)
                write_status_yaml(path, default_rrr_status(injection_version))
            except OSError as exc:
                return "failed", str(exc)
            return "created", "minted summary defaults"
    data, issues = load_status(path)
    if data is None:
        message = issues[0].message if issues else f"invalid {RRR_STATUS_NAME}"
        return "failed", message
    if fill_rrr_status_missing(data, injection_version):
        write_status_yaml(path, data)
        return "fixed", "filled missing keys"
    return "ok", "complete"


def setup_status(
    phase_dir: Path,
    injection_version: int,
    *,
    stems: tuple[str, ...] | None = None,
) -> tuple[str, str]:
    path = phase_dir / STATUS_NAME
    level_stems = stems if stems is not None else stems_for_dir(phase_dir)
    if not path.is_file():
        try:
            write_status_yaml(
                path, default_unfrozen_status(injection_version, stems=level_stems)
            )
        except OSError as exc:
            return "failed", str(exc)
        return "created", "minted unfrozen 0.1.0?"
    data, issues = load_status(path)
    if data is None:
        message = issues[0].message if issues else "invalid status.yaml"
        return "failed", message
    payload_changed, meta_changed = fill_status_missing(
        data, injection_version, stems=level_stems
    )
    hash_missing = "mint_hash" not in data
    if payload_changed or hash_missing:
        data["mint_hash"] = compute_mint_hash(data)
    if payload_changed or meta_changed or hash_missing:
        write_status_yaml(path, data)
        return "fixed", "filled missing keys"
    return "ok", "complete + mint_hash"


def setup_cascade_format(phase_dir: Path) -> tuple[str, str]:
    if not phase_dir.is_dir():
        return "failed", f"{phase_dir} is not a directory"
    stems = stems_for_dir(phase_dir)
    if not has_cascade_docs(phase_dir, stems=stems):
        return "ok", _MSG_NO_CASCADE_DOCS
    before = {
        path.name: path.read_bytes()
        for path in phase_dir.iterdir()
        if path.is_file() and path.stem in stems and path.suffix in {".md", ".yaml"}
    }
    issues = rewrite_planning_dir(phase_dir, empty_ok=True)
    if has_errors(issues):
        return "failed", "; ".join(
            issue.message for issue in issues if issue.severity == "error"
        )
    after = {
        path.name: path.read_bytes()
        for path in phase_dir.iterdir()
        if path.is_file() and path.stem in stems and path.suffix in {".md", ".yaml"}
    }
    if before != after:
        return "fixed", "rewrote list-meta/yaml to canonical md"
    return "ok", _MSG_ALREADY_CANONICAL


def setup_cascade_versioning(phase_dir: Path) -> tuple[str, str]:
    if not phase_dir.is_dir():
        return "failed", f"{phase_dir} is not a directory"
    stems = stems_for_dir(phase_dir)
    md_paths = [
        phase_dir / f"{stem}.md"
        for stem in stems
        if (phase_dir / f"{stem}.md").is_file()
    ]
    if not md_paths:
        return "ok", _MSG_NO_CASCADE_DOCS
    status: dict[str, Any] | None = None
    status_path = find_status_path(phase_dir)
    if status_path is not None:
        status, _ = load_status(status_path)
    outcomes: list[str] = []
    messages: list[str] = []
    for path in md_paths:
        try:
            text = path.read_text(encoding="utf-8")
            new_text, outcome = ensure_doc_frontmatter(text, path.stem, status)
            if outcome != "ok":
                path.write_text(new_text, encoding="utf-8")
            outcomes.append(outcome)
        except (OSError, yaml.YAMLError) as exc:
            outcomes.append("failed")
            messages.append(f"{path.name}: {exc}")
    if "failed" in outcomes:
        return "failed", "; ".join(messages) or "frontmatter backfill failed"
    if "fixed" in outcomes:
        return "fixed", "dropped stub version / aligned with status"
    if "created" in outcomes:
        return "created", "inserted track/doc_rev/pins/created"
    return "ok", _MSG_ALREADY_CANONICAL


def setup_pr_validate_workflow(repo_root: Path) -> tuple[str, str]:
    """Install PR-scoped validate_planning workflow (fail closed on HAND_BUMP)."""
    try:
        template = PR_VALIDATE_WORKFLOW_TEMPLATE_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        return "failed", f"missing workflow template: {exc}"
    if not template.strip():
        return "failed", "workflow template is empty"
    expected = template if template.endswith("\n") else template + "\n"
    path = repo_root / PR_VALIDATE_WORKFLOW_REL
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file():
            path.write_text(expected, encoding="utf-8")
            return "created", "wrote PR validate workflow"
        current = path.read_text(encoding="utf-8")
        if current == expected:
            return "ok", "matches template"
        path.write_text(expected, encoding="utf-8")
        return "fixed", "overwrote to template"
    except OSError as exc:
        return "failed", str(exc)


def _merge_cascade_outcomes(
    outcomes: list[tuple[str, str]],
) -> tuple[str, str]:
    if any(status == "failed" for status, _ in outcomes):
        messages = [msg for status, msg in outcomes if status == "failed"]
        return "failed", "; ".join(messages)
    if any(status == "fixed" for status, _ in outcomes):
        return "fixed", "rewrote or aligned cascade docs"
    if any(status == "created" for status, _ in outcomes):
        return "created", "inserted track/doc_rev/pins/created"
    if all(msg == _MSG_NO_CASCADE_DOCS for _, msg in outcomes):
        return "ok", _MSG_NO_CASCADE_DOCS
    return "ok", _MSG_ALREADY_CANONICAL


def run_setup(docs: Path, repo_root: Path) -> int:
    """Framework setup: docs/rr/{track}/{phase}/, parking, rrr-status, dual statuses."""
    try:
        safe_docs = resolve_within_root(docs, repo_root)
    except ValueError as exc:
        print(f"docs root\tfailed\t{exc}")
        return 1
    results: list[tuple[str, str, str]] = []
    results.append(("docs root", *setup_mkdir(safe_docs, repo_root)))
    rr = rr_root(safe_docs)
    results.append(("rr directory", *setup_mkdir(rr, repo_root)))
    results.append(("layout migrate", *migrate_docs_layout(safe_docs)))
    results.append(("tasks directory", *setup_mkdir(tasks_dir(safe_docs), repo_root)))
    track = current_track(safe_docs)
    discovery = track_phase_dir(safe_docs, track, DISCOVERY_DIR)
    plan = track_phase_dir(safe_docs, track, PLAN_DIR)
    results.append(("discovery directory", *setup_mkdir(discovery, repo_root)))
    results.append(("plan directory", *setup_mkdir(plan, repo_root)))
    try:
        version, load_line, body = parse_agent_config()
        config_error: str | None = None
    except (OSError, ValueError, yaml.YAMLError) as exc:
        version, load_line, body = 0, "", ""
        config_error = str(exc)
    if config_error is not None:
        results.append(("root SoT load line", "failed", config_error))
        results.append((AGENT_PLAN_NAME, "failed", config_error))
        results.append((RRR_STATUS_NAME, "failed", config_error))
        results.append(("discovery status.yaml", "failed", config_error))
        results.append(("plan status.yaml", "failed", config_error))
    else:
        results.append(("root SoT load line", *setup_root_sot(repo_root, load_line)))
        results.append((AGENT_PLAN_NAME, *setup_agent_plan(safe_docs, body)))
        results.append((RRR_STATUS_NAME, *setup_rrr_status(safe_docs, version)))
        results.append(
            (
                "discovery status.yaml",
                *setup_status(discovery, version, stems=DISCOVERY_STEMS),
            )
        )
        results.append(
            ("plan status.yaml", *setup_status(plan, version, stems=PLAN_STEMS))
        )
    format_outcomes = [
        setup_cascade_format(discovery),
        setup_cascade_format(plan),
    ]
    version_outcomes = [
        setup_cascade_versioning(discovery),
        setup_cascade_versioning(plan),
    ]
    results.append(("cascade format", *_merge_cascade_outcomes(format_outcomes)))
    results.append(("cascade versioning", *_merge_cascade_outcomes(version_outcomes)))
    results.append(("pr validate workflow", *setup_pr_validate_workflow(repo_root)))
    by_name = {name: (status, message) for name, status, message in results}
    failed = False
    for name in SETUP_SECTIONS:
        status, message = by_name[name]
        print(f"{name}\t{status}\t{message}")
        if status == "failed":
            failed = True
    return 1 if failed else 0
