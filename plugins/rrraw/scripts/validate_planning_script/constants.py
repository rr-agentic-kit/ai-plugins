"""Regexes, enums, path constants."""

from __future__ import annotations

import re
from pathlib import Path

DOC_STEMS: tuple[str, ...] = ("exec-summary", "mrd", "brd", "prd", "frd")
YAML_SKIP_KEYS = frozenset(
    {
        "title",
        "body",
        "doc_type",
        "version",
        "created",
        "traces_from",
        "item_index",
        "track",
        "doc_rev",
        "pins",
    }
)
CANONICAL_KEY_ORDER: tuple[str, ...] = (
    "parent",
    "kind",
    "spec",
    "build",
    "moscow",
    "kano",
    "if-present",
    "if-absent",
    "if-wrong",
    "class",
    "rationale",
    "supersedes",
    "superseded-by",
)
EM_DASH = "\u2014"
NATIVE_INDEX_COL: dict[str, str] = {
    "exec-summary": "MoSCoW",
    "mrd": "Kano",
    "brd": "MoSCoW",
    "prd": "MoSCoW",
    "frd": "Class",
}

PREFIX_TO_DOC: dict[str, str] = {
    "ES": "exec-summary",
    "MRD": "mrd",
    "BRD": "brd",
    "PRD": "prd",
    "FRD": "frd",
}

DOC_TO_PREFIX: dict[str, str] = {v: k for k, v in PREFIX_TO_DOC.items()}
PREFIX_LEVEL: dict[str, int] = {"ES": 0, "MRD": 1, "BRD": 2, "PRD": 3, "FRD": 4}
DOC_METHOD: dict[str, str] = {
    "exec-summary": "moscow",
    "mrd": "kano",
    "brd": "moscow",
    "prd": "moscow",
    "frd": "triad",
}

HEADING_RE = re.compile(r"^(#{2,4}) (ES|MRD|BRD|PRD|FRD)-(\d+(?:\.\d+)?): (.+)$")
LIST_META_RE = re.compile(r"^- \*\*([^*\n]+):\*\* ([^\n]+)$")
INLINE_KEY_RE = re.compile(r"^_([a-z][a-z0-9-]*)_:\s*([^\n]*)$")
META_SPLIT_RE = re.compile(r"\s+\|\s+(?=_[a-z][a-z0-9-]*_:)")
BODY_QUOTE_RE = re.compile(r"^> ?(.*)$")
ATX_HEADING_RE = re.compile(r"^#{1,6} ")
ID_RE = re.compile(r"^(ES|MRD|BRD|PRD|FRD)-(\d+)(?:\.(\d+))?$")
RATIONALE_RE = re.compile(r"^r-\d{3,}$")
EVIDENCE_ID_RE = re.compile(r"^e-\d{3,}$")
LEDGER_NAME = "decision-ledger.yaml"
FLIP_KINDS = frozenset({"metric", "fact", "event"})
CONDITION_STRENGTHS = frozenset({"measurable", "observable", "vague"})
RATIONALE_DECISIONS = frozenset({"accept", "reject", "postpone", "pivot"})
RATIONALE_STATUSES = frozenset({"live", "invalidated", "superseded"})
EVIDENCE_STATUSES = frozenset({"supported", "refuted", "unknown", "superseded"})
METRIC_OPS = frozenset({"<", "<=", ">", ">=", "==", "!="})
QUEUE_STATUSES = frozenset({"open", "decided", "dismissed"})
_DASH_CLASS = "\u2014\u2013\u2212-"
AXIS_RE = re.compile(
    rf"^(critical|high|moderate|low)\s+[{_DASH_CLASS}]\s+(.+)$",
    re.IGNORECASE,
)

CLOSED_KEYS = frozenset(CANONICAL_KEY_ORDER)
REQUIRED_KEYS = frozenset({"parent", "kind", "spec"})
FRD_LEAF_KEYS = frozenset({"build", "if-present", "if-absent", "if-wrong", "class"})
YAML_KEY_MAP: dict[str, str] = {
    "Parent": "parent",
    "Kind": "kind",
    "Spec": "spec",
    "Build": "build",
    "MoSCoW": "moscow",
    "Kano": "kano",
    "If present": "if-present",
    "If absent": "if-absent",
    "If wrong": "if-wrong",
    "Class": "class",
    "Rationale": "rationale",
    "Supersedes": "supersedes",
    "Superseded-by": "superseded-by",
}
KIND_VALUES = frozenset({"container", "leaf"})
SPEC_VALUES = frozenset({"idea", "draft", "ready", "deprecated"})
BUILD_VALUES = frozenset({"none", "in_progress", "done"})
MOSCOW_VALUES = frozenset({"Must", "Should", "Could", "Won't"})
KANO_VALUES = frozenset({"basic", "performance", "delighter"})
MAGNITUDE_VALUES = frozenset({"critical", "high", "moderate", "low"})
CLASS_VALUES = frozenset(
    {"must-correct", "must-present", "protect", "leverage", "optional"}
)
HIGH_MAG = frozenset({"critical", "high"})
NULL_SENTINELS = frozenset({"\u2014", "-", "\u2013", "\u2212", "null", ""})
JSON_ITEM_KEYS = frozenset(
    {
        "id",
        "parent",
        "kind",
        "spec",
        "build",
        "supersedes",
        "superseded_by",
        "priority_method",
        "moscow",
        "kano",
        "triad",
        "rationale",
        "title",
        "doc",
    }
)

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    PLUGIN_ROOT / "skills" / "rr-planner" / "refs" / "schemas" / "items.schema.json"
)
AGENT_CONFIG_PATH = PLUGIN_ROOT / "skills" / "rr-planner" / "refs" / "agent-config.md"

AGENT_PLAN_NAME = "agent.plan.md"
AGENT_PLAN_TEMPLATE_PATH = AGENT_CONFIG_PATH.with_name(AGENT_PLAN_NAME)
STATUS_NAME = "status.yaml"
FUTURE_NAME = "future.md"
CHALLENGE_STATUSES = frozenset({"dirty", "clean", "dirty-accepted"})
CHALLENGE_KEYS = ("challenge", "next_challenge")
MINT_EXCLUDED_KEYS = frozenset(
    {
        "claude_config_version",
        "mint_hash",
        "product_status",
        "challenge",
        "next_challenge",
    }
)
ROOT_SOT_FILENAMES: frozenset[str] = frozenset(
    {"CLAUDE.md", "AGENTS.md", "GEMINI.md", "CODEX.md", "CURSOR.md"}
)
PARENT_DOC: dict[str, str] = {
    "mrd": "exec-summary",
    "brd": "mrd",
    "prd": "brd",
    "frd": "prd",
}
TRACK_DIR_RE = re.compile(r"^\d+\.\d+$")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
INJECTION_FENCE_RE = re.compile(r"```yaml\n(injection:.*?)\n```", re.DOTALL)
_CREATED_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_CREATED_TIME_RE = re.compile(r"^[T ]\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:?\d{2})?$")


def matches_created_ts(value: str) -> bool:
    stamp = value.strip()
    if _CREATED_DATE_RE.fullmatch(stamp):
        return True
    if len(stamp) <= 10:
        return False
    return _CREATED_DATE_RE.fullmatch(stamp[:10]) is not None and (
        _CREATED_TIME_RE.fullmatch(stamp[10:]) is not None
    )


CREATED_TS_RE = _CREATED_DATE_RE
STUB_FRONTMATTER_KEYS = frozenset({"version", "traces_from"})
SETUP_SECTIONS: tuple[str, ...] = (
    "plans directory",
    "root SoT load line",
    AGENT_PLAN_NAME,
    "status.yaml",
    "cascade format",
    "cascade versioning",
)
FRONTMATTER_KEYS: tuple[str, ...] = (
    "doc_type",
    "track",
    "doc_rev",
    "pins",
    "created",
)
