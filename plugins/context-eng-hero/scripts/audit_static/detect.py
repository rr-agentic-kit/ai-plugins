from __future__ import annotations

from pathlib import Path


def _detect_skill_type(parts: tuple[str, ...], name: str) -> str | None:
    if len(parts) >= 3 and parts[0] == "skills" and name == "readme.md":
        return "skill-readme"
    # skills/<name>/refs/**/*.md  (incl. doc-standards/)
    if (
        len(parts) >= 4
        and parts[0] == "skills"
        and parts[2] in {"refs", "references"}
        and name.endswith(".md")
    ):
        return "ref-file"
    if len(parts) >= 2 and parts[0] == "skills" and name == "skill.md":
        return "skill"
    return None


def _detect_markdown_type(parts: tuple[str, ...], name: str, stem: str) -> str | None:
    if parts and parts[0] == "commands" and name.endswith(".md"):
        return "command"
    if parts and parts[0] == "agents" and name.endswith(".md"):
        return "agent"
    if name.endswith(".mdc") or (parts and parts[0] in {".cursor", "rules"}):
        return "rule"
    if "workflow" in stem.lower():
        return "workflow"
    if parts and parts[0] == "docs" and name.endswith(".md"):
        return "workflow"
    return None


def detect_type(rel_path: Path) -> str:
    parts = rel_path.parts
    name = rel_path.name.lower()
    if skill_type := _detect_skill_type(parts, name):
        return skill_type
    if md_type := _detect_markdown_type(parts, name, rel_path.stem):
        return md_type
    return "unknown"
