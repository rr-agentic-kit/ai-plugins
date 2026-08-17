"""Issue, Axis, Triad, Item."""

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
class Axis:
    effect: str
    magnitude: str

    def to_record(self) -> dict[str, str]:
        return {"effect": self.effect, "magnitude": self.magnitude}


@dataclass
class Triad:
    if_present: Axis
    if_absent: Axis
    if_wrong: Axis
    class_name: str

    def to_record(self) -> dict[str, Any]:
        return {
            "if_present": self.if_present.to_record(),
            "if_absent": self.if_absent.to_record(),
            "if_wrong": self.if_wrong.to_record(),
            "class": self.class_name,
        }


@dataclass
class Item:
    id: str
    title: str
    prefix: str
    doc: str
    parent: str | None
    kind: str
    spec: str
    build: str | None = None
    moscow: str | None = None
    kano: str | None = None
    triad: Triad | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    rationale: str | None = None
    source_file: str = ""
    raw_keys: set[str] = field(default_factory=set)
    raw_meta: dict[str, str] = field(default_factory=dict)

    @property
    def parts(self) -> tuple[int, ...]:
        match = ID_RE.match(self.id)
        if not match:
            return ()
        major = int(match.group(2))
        minor = match.group(3)
        if minor is None:
            return (major,)
        return (major, int(minor))

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
        if self.build is not None:
            record["build"] = self.build
        if self.supersedes:
            record["supersedes"] = self.supersedes
        if self.superseded_by:
            record["superseded_by"] = self.superseded_by
        if self.rationale:
            record["rationale"] = self.rationale
        method = DOC_METHOD[self.doc]
        if self.kind == "leaf":
            if method == "moscow":
                record["moscow"] = self.moscow
            elif method == "kano":
                record["kano"] = self.kano
            elif self.triad is not None:
                record["triad"] = self.triad.to_record()
        return record


def has_errors(issues: list[Issue]) -> bool:
    return any(issue.severity == "error" for issue in issues)
