"""Detects whether a shell command line runs a branch-mutating git write.

Policy: on a protected branch (master/main) the only allowed writable git
action is `tag` — everything that can move the branch tip or rewrite its
history (commit, merge, rebase, cherry-pick, revert, reset, am, pull) is
blocked. This is a curated blocklist, not a full allowlist of git
subcommands, so read-only/staging commands (status, diff, log, add, stash,
branch, fetch, tag, ...) are never touched by this module.
"""

from __future__ import annotations

import re
import shlex
from pathlib import PurePosixPath

BLOCKED_WRITE_SUBCOMMANDS = frozenset(
    {"commit", "merge", "rebase", "cherry-pick", "revert", "reset", "am", "pull"}
)

_SEGMENT_BREAKS = frozenset({"&&", "||", ";", "|", "&", "(", ")"})
_SHELL_WRAPPERS = frozenset({"bash", "sh", "zsh", "dash"})
_SHELL_WRAPPER_FLAGS = frozenset({"-c", "-lc", "-cx", "-xc"})
_WRAPPER_PREFIXES = frozenset({"sudo", "command", "exec"})
_GIT_GLOBAL_OPTS_WITH_VALUE = frozenset(
    {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
)
_BLOCKED_FALLBACK_RE = re.compile(
    r"\bgit\s+(" + "|".join(re.escape(s) for s in BLOCKED_WRITE_SUBCOMMANDS) + r")\b"
)
_MAX_WRAPPER_DEPTH = 3
UNKNOWN_BLOCKED_SUBCOMMAND = "<git-write>"


def tokenize_segments(command: str) -> list[list[str]]:
    """Split a shell command line into argv segments on &&/||/;/|/&/(/).

    Raises ValueError on unbalanced quotes (propagated to the caller).
    """
    lexer = shlex.shlex(command, posix=True, punctuation_chars="&|;()<>")
    lexer.whitespace_split = True
    tokens = list(lexer)

    segments: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token in _SEGMENT_BREAKS:
            if current:
                segments.append(current)
                current = []
            continue
        current.append(token)
    if current:
        segments.append(current)
    return segments


def _basename(token: str) -> str:
    return PurePosixPath(token).name


def git_subcommand(argv: list[str]) -> str | None:
    """Return the git subcommand token in argv, or None if not a git invocation."""
    if not argv:
        return None
    if _basename(argv[0]) != "git":
        return None
    i = 1
    while i < len(argv):
        token = argv[i]
        if token == "--":
            i += 1
            continue
        if token.startswith("-"):
            base = token.split("=", 1)[0]
            if base in _GIT_GLOBAL_OPTS_WITH_VALUE and "=" not in token:
                i += 2
                continue
            i += 1
            continue
        return token
    return None


def segment_blocked_subcommand(argv: list[str]) -> str | None:
    if argv and _basename(argv[0]) in _WRAPPER_PREFIXES:
        argv = argv[1:]
    sub = git_subcommand(argv)
    return sub if sub in BLOCKED_WRITE_SUBCOMMANDS else None


def expand_shell_wrapper(argv: list[str]) -> str | None:
    if len(argv) < 3:
        return None
    if _basename(argv[0]) not in _SHELL_WRAPPERS:
        return None
    if argv[1] not in _SHELL_WRAPPER_FLAGS:
        return None
    return argv[2]


def find_blocked_subcommand(command: str, *, _depth: int = 0) -> str | None:
    """The blocked git subcommand `command` would run, or None if none.

    On tokenizer failure (unbalanced quotes) this falls back to a substring
    regex rather than failing open: an unparseable command is treated as
    "maybe a blocked write," since a false block is far cheaper than letting
    a real branch mutation onto a protected branch slip through.
    """
    if _depth > _MAX_WRAPPER_DEPTH:
        return UNKNOWN_BLOCKED_SUBCOMMAND
    try:
        segments = tokenize_segments(command)
    except ValueError:
        match = _BLOCKED_FALLBACK_RE.search(command)
        return match.group(1) if match else None

    for argv in segments:
        blocked = segment_blocked_subcommand(argv)
        if blocked is not None:
            return blocked
        nested = expand_shell_wrapper(argv)
        if nested is not None:
            nested_blocked = find_blocked_subcommand(nested, _depth=_depth + 1)
            if nested_blocked is not None:
                return nested_blocked
    return None
