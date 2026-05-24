from __future__ import annotations

from pathlib import Path


def detect_type(plugin_root: Path, rel_path: Path) -> str:
    parts = rel_path.parts
    name = rel_path.name.lower()
    if len(parts) >= 2 and parts[0] == "skills" and name == "skill.md":
        return "skill"
    if parts and parts[0] == "commands" and name.endswith(".md"):
        return "command"
    if parts and parts[0] == "agents" and name.endswith(".md"):
        return "agent"
    if name.endswith(".mdc") or (parts and parts[0] in {".cursor", "rules"}):
        return "rule"
    if "workflow" in rel_path.stem.lower():
        return "workflow"
    return "workflow"
