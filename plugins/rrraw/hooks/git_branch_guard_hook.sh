#!/bin/sh
# Dual-runtime adapter: Cursor + Claude Code → git_branch_guard --hook → deny JSON.
# Usage: git_branch_guard_hook.sh --runtime cursor|claude
# Fail-open covers infra only (missing script/interpreter). A real deny is
# expressed as exit-0 + JSON on stdout (both hosts' schemas work this way),
# so `|| exit 0` below can never suppress a genuine block.
set -eu

RUNTIME=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --runtime)
      RUNTIME=${2:-}
      shift 2
      ;;
    --runtime=*)
      RUNTIME=${1#--runtime=}
      shift
      ;;
    *)
      shift
      ;;
  esac
done

case "$RUNTIME" in
  cursor|claude) ;;
  *)
    # Unknown runtime — fail-open
    exit 0
    ;;
esac

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PLUGIN_ROOT=$(CDPATH= cd -- "$HERE/.." && pwd)
CLI="$PLUGIN_ROOT/scripts/git_branch_guard.sh"

# Prefer CLAUDE_PLUGIN_ROOT when set (Claude install); else sibling of hooks/
if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -x "$CLAUDE_PLUGIN_ROOT/scripts/git_branch_guard.sh" ]; then
  CLI="$CLAUDE_PLUGIN_ROOT/scripts/git_branch_guard.sh"
fi

if [ ! -x "$CLI" ] && [ -f "$CLI" ]; then
  chmod +x "$CLI" 2>/dev/null || true
fi
if [ ! -f "$CLI" ]; then
  exit 0
fi

# Forward host stdin; reuse git_branch_guard.sh Python resolution.
"$CLI" --hook --runtime "$RUNTIME" || exit 0
