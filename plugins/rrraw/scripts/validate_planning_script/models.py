"""Issue and Item."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .constants import DOC_METHOD, ID_RE


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    item_id: str | None = None

    def format(self) -> str:
        loc = f" {self.item_id}" if self.item_id else ""
        label = "ERROR" if self.severity == "error" else "WARN"
        return f"{label} [{self.code}]{loc}: {self.message}"

    @classmethod
    def error(cls, code: str, msg: str, item_id: str | None = None) -> Issue:
        return cls("error", code, msg, item_id)

    @classmethod
    def warn(cls, code: str, msg: str, item_id: str | None = None) -> Issue:
        return cls("warning", code, msg, item_id)


@dataclass
class Item:
    id: str
    title: str
    prefix: str
    doc: str
    parent: str | None
    kind: str
    spec: str
    status: str | None = None
    priority: str | None = None
    tag: str | None = None
    goal_type: str | None = None
    reach: str | None = None
    impact: str | None = None
    confidence: str | None = None
    effort: str | None = None
    moscow: str | None = None
    kano: str | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    rationale: str | None = None
    source_file: str = ""
    raw_keys: set[str] = field(default_factory=set)
    raw_meta: dict[str, str] = field(default_factory=dict)

    @property
    def parts(self) -> tuple[int, int]:
        match = ID_RE.match(self.id)
        if not match:
            return (0, 0)
        major = int(match.group(2))
        minor_raw = match.group(3)
        minor = int(minor_raw) if minor_raw is not None else 0
        return (major, minor)

    @property
    def is_nested(self) -> bool:
        return self.parts[1] > 0

    def to_record(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "id": self.id,
            "parent": self.parent,
            "kind": self.kind,
            "spec": self.spec,
            "priority_method": DOC_METHOD[self.doc],
            "title": self.title,
            "doc": self.doc,
        }
        if self.status is not None:
            record["status"] = self.status
        if self.priority is not None:
            record["priority"] = self.priority
        if self.tag is not None:
            record["tag"] = self.tag
        if self.supersedes:
            record["supersedes"] = self.supersedes
        if self.superseded_by:
            record["superseded_by"] = self.superseded_by
        if self.rationale:
            record["rationale"] = self.rationale
        if self.kind == "leaf":
            _apply_leaf_priority_fields(record, DOC_METHOD[self.doc], self)
        return record


def _apply_leaf_priority_fields(
    record: dict[str, Any], method: str, item: Item
) -> None:
    if method == "moscow":
        record["moscow"] = item.moscow
    elif method == "kano":
        record["kano"] = item.kano
    elif method == "rice":
        if item.goal_type is not None:
            record["goal_type"] = item.goal_type
        if item.reach is not None:
            record["reach"] = item.reach
        if item.impact is not None:
            record["impact"] = item.impact
        if item.confidence is not None:
            record["confidence"] = item.confidence
        if item.effort is not None:
            record["effort"] = item.effort


def has_errors(issues: list[Issue]) -> bool:
    return any(issue.severity == "error" for issue in issues)
