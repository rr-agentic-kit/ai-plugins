#!/bin/sh
# Dual-runtime adapter: Cursor + Claude Code → context_budget --hook → inject JSON.
# Usage: context_budget_hook.sh --runtime cursor|claude
# Fail-open: missing deps / parse errors → exit 0 silent.
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
CLI="$PLUGIN_ROOT/scripts/context_budget.sh"

# Prefer CLAUDE_PLUGIN_ROOT when set (Claude install); else sibling of hooks/
if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -x "$CLAUDE_PLUGIN_ROOT/scripts/context_budget.sh" ]; then
  CLI="$CLAUDE_PLUGIN_ROOT/scripts/context_budget.sh"
fi

if [ ! -x "$CLI" ] && [ -f "$CLI" ]; then
  chmod +x "$CLI" 2>/dev/null || true
fi
if [ ! -f "$CLI" ]; then
  exit 0
fi

# Forward host stdin; reuse context_budget.sh Python/tiktoken resolution.
"$CLI" --hook --runtime "$RUNTIME" || exit 0
