"""Regexes, enums, path constants."""

from __future__ import annotations

import re
from pathlib import Path

DISCOVERY_STEMS: tuple[str, ...] = ("executive-summary", "mrd", "brd")
PLAN_STEMS: tuple[str, ...] = ("prd",)
DOC_STEMS: tuple[str, ...] = (*DISCOVERY_STEMS, *PLAN_STEMS)
# Legacy stem accepted on read / migrate; writers emit DOC_STEMS only.
LEGACY_DOC_STEMS: dict[str, str] = {"exec-summary": "executive-summary"}
DOCS_ROOT_NAME = "docs"
RRR_STATUS_NAME = "rrr-status.yaml"
DISCOVERY_DIR = "discovery"
PLAN_DIR = "plan"
LEGACY_PLANS_DIR = "plans"
LEGACY_PLANNING_DIR = "planning"
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
    "status",
    "priority",
    "tag",
    "goal-type",
    "reach",
    "impact",
    "confidence",
    "effort",
    "moscow",
    "kano",
    "rationale",
    "supersedes",
    "superseded-by",
)
EM_DASH = "\u2014"
NATIVE_INDEX_COL: dict[str, str] = {
    "executive-summary": "MoSCoW",
    "mrd": "Kano",
    "brd": "MoSCoW",
    "prd": "RICE",
}

PREFIX_TO_DOC: dict[str, str] = {
    "ES": "executive-summary",
    "MRD": "mrd",
    "BRD": "brd",
    "PRD": "prd",
}

DOC_TO_PREFIX: dict[str, str] = {v: k for k, v in PREFIX_TO_DOC.items()}
PREFIX_LEVEL: dict[str, int] = {"ES": 0, "MRD": 1, "BRD": 2, "PRD": 3}
DOC_METHOD: dict[str, str] = {
    "executive-summary": "moscow",
    "mrd": "kano",
    "brd": "moscow",
    "prd": "rice",
}

HEADING_RE = re.compile(r"^(#{2,4}) (ES|MRD|BRD|PRD)-(\d+(?:\.\d+)?): (.+)$")
LIST_META_RE = re.compile(r"^- \*\*([^*\n]+):\*\* ([^\n]+)$")
INLINE_KEY_RE = re.compile(r"^_([a-z][a-z0-9-]*)_:\s*")
META_SPLIT_RE = re.compile(r"\s+\|\s+(?=_[a-z][a-z0-9-]*_:)")
BODY_QUOTE_RE = re.compile(r"^> ?(.*)$")
ATX_HEADING_RE = re.compile(r"^#{1,6} ")
ID_RE = re.compile(r"^(ES|MRD|BRD|PRD)-(\d+)(?:\.(\d+))?$")
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

CLOSED_KEYS = frozenset(CANONICAL_KEY_ORDER)
REQUIRED_KEYS = frozenset({"parent", "kind", "spec"})
YAML_KEY_MAP: dict[str, str] = {
    "Parent": "parent",
    "Kind": "kind",
    "Spec": "spec",
    "Status": "status",
    "Priority": "priority",
    "Tag": "tag",
    "Goal-type": "goal-type",
    "Reach": "reach",
    "Impact": "impact",
    "Confidence": "confidence",
    "Effort": "effort",
    "MoSCoW": "moscow",
    "Kano": "kano",
    "Rationale": "rationale",
    "Supersedes": "supersedes",
    "Superseded-by": "superseded-by",
}
KIND_VALUES = frozenset({"container", "leaf"})
SPEC_VALUES = frozenset({"idea", "draft", "ready", "deprecated"})
MOSCOW_VALUES = frozenset({"Must", "Should", "Could", "Won't"})
KANO_VALUES = frozenset({"basic", "performance", "delighter"})
IMPACT_VALUES = frozenset({"0.25", "0.5", "1", "2", "3"})
CONFIDENCE_VALUES = frozenset({"low", "medium", "high"})
EFFORT_VALUES = frozenset({"1", "2", "3", "5", "8", "13"})
GOAL_TYPE_VALUES = frozenset({"primary", "support"})
STATUS_VALUES = frozenset({"deferred", "selected", "in_progress", "delivered"})
PRIORITY_VALUES = frozenset({"P1", "P2", "P3"})
RICE_FACTOR_KEYS = frozenset({"reach", "impact", "confidence", "effort"})
NULL_SENTINELS = frozenset({"\u2014", "-", "\u2013", "\u2212", "null", ""})
JSON_ITEM_KEYS = frozenset(
    {
        "id",
        "parent",
        "kind",
        "spec",
        "status",
        "priority",
        "tag",
        "goal_type",
        "reach",
        "impact",
        "confidence",
        "effort",
        "supersedes",
        "superseded_by",
        "priority_method",
        "moscow",
        "kano",
        "rationale",
        "title",
        "doc",
    }
)

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PLUGIN_ROOT / "refs" / "planning" / "schemas" / "items.schema.json"
AGENT_CONFIG_PATH = PLUGIN_ROOT / "refs" / "planning" / "agent-config.md"

AGENT_PLAN_NAME = "agent.plan.md"
AGENT_PLAN_TEMPLATE_PATH = AGENT_CONFIG_PATH.with_name(AGENT_PLAN_NAME)
STATUS_NAME = "status.yaml"
FUTURE_NAME = "future.md"
TECH_NAME = "tech.md"
LATER_NAME = "later.md"
PHASE_DIRS: tuple[str, ...] = (DISCOVERY_DIR, PLAN_DIR)
PHASE_STEMS: dict[str, tuple[str, ...]] = {
    DISCOVERY_DIR: DISCOVERY_STEMS,
    PLAN_DIR: PLAN_STEMS,
}
BUSINESS_CASE_NAME = "business-case.yaml"
# Compact Plan handoff — required keys (omtm / positioning_angle optional).
BUSINESS_CASE_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {
        "vision",
        "problem",
        "premises",
        "viability_verdict",
        "north_star",
        "input_metrics",
        "cost_position",
        "defensibility",
        "market_read",
        "beachhead_icp",
        "objectives",
        "stakeholders",
        "capabilities",
        "constraints",
        "non_goals",
        "gtm_motion",
        "open_holds",
        "artifact_refs",
        "ledger_pins",
    }
)
CHALLENGE_STATUSES = frozenset({"dirty", "clean", "dirty-accepted"})
CHALLENGE_KEYS = ("challenge", "next_challenge")
MINT_EXCLUDED_KEYS = frozenset(
    {
        "claude_config_version",
        "mint_hash",
        "product_status",
        "challenge",
        "next_challenge",
        "discovery_complete",
    }
)
ROOT_SOT_FILENAMES: frozenset[str] = frozenset(
    {"CLAUDE.md", "AGENTS.md", "GEMINI.md", "CODEX.md", "CURSOR.md"}
)
PARENT_DOC: dict[str, str] = {
    "mrd": "executive-summary",
    "brd": "mrd",
    "prd": "brd",
}


def canonicalize_doc_stem(stem: str | None) -> str | None:
    """Map legacy stems to canonical DOC_STEMS; pass through known stems."""
    if stem is None:
        return None
    if stem in LEGACY_DOC_STEMS:
        return LEGACY_DOC_STEMS[stem]
    if stem in DOC_STEMS:
        return stem
    return stem


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
    "docs root",
    "discovery directory",
    "plan directory",
    "root SoT load line",
    AGENT_PLAN_NAME,
    RRR_STATUS_NAME,
    "discovery status.yaml",
    "plan status.yaml",
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
