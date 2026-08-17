"""--setup, agent.plan.md, root SoT load line."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .constants import (
    AGENT_CONFIG_PATH,
    AGENT_PLAN_NAME,
    AGENT_PLAN_TEMPLATE_PATH,
    DOC_STEMS,
    INJECTION_FENCE_RE,
    ROOT_SOT_FILENAMES,
    SETUP_SECTIONS,
    STATUS_NAME,
)
from .models import Issue, has_errors
from .rewrite import rewrite_planning_dir
from .workspace import (
    compute_mint_hash,
    default_unfrozen_status,
    ensure_doc_frontmatter,
    fill_status_missing,
    find_status_path,
    has_cascade_docs,
    load_status,
    write_status_yaml,
)


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


def emit_agent_plan(plans_dir: Path, *, body: str | None = None) -> Path:
    plans_dir.mkdir(parents=True, exist_ok=True)
    text = body if body is not None else parse_agent_config()[2]
    path = plans_dir / AGENT_PLAN_NAME
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


def find_repo_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / ".git").exists():
            return candidate
    return start.resolve()


def sync_agent_injection(
    plans_dir: Path,
    repo_root: Path,
    *,
    force: bool = False,
) -> list[Issue]:
    issues: list[Issue] = []
    status_path = plans_dir / STATUS_NAME
    plan_path = plans_dir / AGENT_PLAN_NAME
    if not force and not status_path.is_file() and not plan_path.is_file():
        return issues
    try:
        version, load_line, body = parse_agent_config()
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [Issue.error("HAND_BUMP", f"agent-config.md: {exc}")]
    emit_agent_plan(plans_dir, body=body)
    sync_root_sot(repo_root, load_line)
    if not status_path.is_file():
        return issues
    data, load_issues = load_status(status_path)
    issues.extend(load_issues)
    if data is None:
        return issues
    if data.get("claude_config_version") != version:
        data["claude_config_version"] = version
        write_status_yaml(status_path, data)
    return issues


def setup_plans_directory(plans_dir: Path) -> tuple[str, str]:
    if plans_dir.is_file():
        return "failed", f"{plans_dir} is a file"
    if plans_dir.is_dir():
        return "ok", "exists"
    try:
        plans_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return "failed", str(exc)
    return "created", "mkdir"


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


def setup_agent_plan(plans_dir: Path, body: str) -> tuple[str, str]:
    path = plans_dir / AGENT_PLAN_NAME
    expected = body if body.endswith("\n") else body + "\n"
    if not path.is_file():
        try:
            emit_agent_plan(plans_dir, body=body)
        except OSError as exc:
            return "failed", str(exc)
        return "created", "wrote template"
    current = path.read_text(encoding="utf-8")
    if current == expected:
        return "ok", "matches template"
    try:
        emit_agent_plan(plans_dir, body=body)
    except OSError as exc:
        return "failed", str(exc)
    return "fixed", "overwrote to template"


def setup_status(plans_dir: Path, injection_version: int) -> tuple[str, str]:
    path = plans_dir / STATUS_NAME
    if not path.is_file():
        try:
            write_status_yaml(path, default_unfrozen_status(injection_version))
        except OSError as exc:
            return "failed", str(exc)
        return "created", "minted unfrozen 0.1.0?"
    data, issues = load_status(path)
    if data is None:
        message = issues[0].message if issues else "invalid status.yaml"
        return "failed", message
    payload_changed, meta_changed = fill_status_missing(data, injection_version)
    hash_missing = "mint_hash" not in data
    if payload_changed or hash_missing:
        data["mint_hash"] = compute_mint_hash(data)
    if payload_changed or meta_changed or hash_missing:
        write_status_yaml(path, data)
        return "fixed", "filled missing keys"
    return "ok", "complete + mint_hash"


def setup_cascade_format(plans_dir: Path) -> tuple[str, str]:
    if not plans_dir.is_dir():
        return "failed", f"{plans_dir} is not a directory"
    if not has_cascade_docs(plans_dir):
        return "ok", "no cascade docs"
    before = {
        path.name: path.read_bytes()
        for path in plans_dir.iterdir()
        if path.is_file() and path.stem in DOC_STEMS and path.suffix in {".md", ".yaml"}
    }
    issues = rewrite_planning_dir(plans_dir, empty_ok=True)
    if has_errors(issues):
        return "failed", "; ".join(
            issue.message for issue in issues if issue.severity == "error"
        )
    after = {
        path.name: path.read_bytes()
        for path in plans_dir.iterdir()
        if path.is_file() and path.stem in DOC_STEMS and path.suffix in {".md", ".yaml"}
    }
    if before != after:
        return "fixed", "rewrote list-meta/yaml to canonical md"
    return "ok", "already canonical"


def setup_cascade_versioning(plans_dir: Path) -> tuple[str, str]:
    if not plans_dir.is_dir():
        return "failed", f"{plans_dir} is not a directory"
    md_paths = [
        plans_dir / f"{stem}.md"
        for stem in DOC_STEMS
        if (plans_dir / f"{stem}.md").is_file()
    ]
    if not md_paths:
        return "ok", "no cascade docs"
    status: dict[str, Any] | None = None
    status_path = find_status_path(plans_dir)
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
    return "ok", "already canonical"


def run_setup(plans_dir: Path, repo_root: Path) -> int:
    results: list[tuple[str, str, str]] = []
    results.append(("plans directory", *setup_plans_directory(plans_dir)))
    try:
        version, load_line, body = parse_agent_config()
        config_error: str | None = None
    except (OSError, ValueError, yaml.YAMLError) as exc:
        version, load_line, body = 0, "", ""
        config_error = str(exc)
    if config_error is not None:
        results.append(("root SoT load line", "failed", config_error))
        results.append(("agent.plan.md", "failed", config_error))
        results.append(("status.yaml", "failed", config_error))
    else:
        results.append(("root SoT load line", *setup_root_sot(repo_root, load_line)))
        results.append(("agent.plan.md", *setup_agent_plan(plans_dir, body)))
        results.append(("status.yaml", *setup_status(plans_dir, version)))
    results.append(("cascade format", *setup_cascade_format(plans_dir)))
    results.append(("cascade versioning", *setup_cascade_versioning(plans_dir)))
    by_name = {name: (status, message) for name, status, message in results}
    failed = False
    for name in SETUP_SECTIONS:
        status, message = by_name[name]
        print(f"{name}\t{status}\t{message}")
        if status == "failed":
            failed = True
    return 1 if failed else 0
