"""Thresholds and fingerprints for auto-learn drift detection."""

from __future__ import annotations

import re
from pathlib import Path

# Scratch under user project / workspace cwd (not plugin install tree).
SCRATCH_REL = Path(".ai") / "learning" / "ce-auto-learn"
EVENTS_NAME = "events.jsonl"
STATE_NAME = "state.json"

# Signal thresholds (high bar — not every stop).
THRASH_WINDOW = 8
THRASH_MIN = 6
REREAD_MIN = 3
EXTREME_REREAD = 6
EXTREME_THRASH = 12
BASH_INFO_MIN = 3
ORPHAN_TTL_DAYS = 7

MESSAGE_CAP = 2_000

# Active-session resource caps (CWE-770) — TTL alone does not bound growth.
MAX_EVENTS = 500
MAX_EVENTS_BYTES = 512_000
MAX_USER_TEXT = 4_000

# Protocol tool names (host hook payloads).
TOOL_READ = "Read"
SHELL_TOOLS = frozenset({"Bash", "Shell"})

# Tools treated as exploration (no write) for thrash.
EXPLORE_TOOLS = frozenset(
    {
        TOOL_READ,
        "Grep",
        "Glob",
        *SHELL_TOOLS,
        "LS",
        "find",
        "rg",
        "SemanticSearch",
    }
)
WRITE_TOOLS = frozenset(
    {
        "Write",
        "Edit",
        "StrReplace",
        "NotebookEdit",
        "Delete",
        "MultiEdit",
    }
)
# Case-insensitive explore membership (bound once; used in thrash loop).
EXPLORE_TOOLS_LOWER = frozenset(t.lower() for t in EXPLORE_TOOLS)

# Bash command fingerprints that look like discovery after skill already bound.
BASH_DISCOVERY_RE = re.compile(
    r"\b(rg|grep|find|cat|ls|tree|head|tail|file|which|type)\b",
    re.I,
)

# Human mid-run correction lexicon (paired with prior thrash).
CORRECTION_RE = re.compile(
    r"\b(wrong|don't|do not|stop doing|you should have|instead of|"
    r"not what i (asked|meant)|incorrect|fix this)\b",
    re.I,
)

# Skill path shapes we prefer to bind.
SKILL_MD_RE = re.compile(
    r"(?:^|/)(?:plugins/[^/]+/skills/[^/]+|"
    r"\.claude/skills/[^/]+|"
    r"\.agents/skills/[^/]+|"
    r"skills/[^/]+)/SKILL\.md$",
    re.I,
)

CACHE_MARKERS = (
    "/.claude/plugins/cache/",
    "/.cursor/plugins/cache/",
)
