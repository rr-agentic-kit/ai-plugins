#!/bin/sh
# Dual-runtime adapter: Cursor + Claude Code → auto_learn --hook → inject JSON.
# Usage: auto_learn_hook.sh --runtime cursor|claude
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
    exit 0
    ;;
esac

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PLUGIN_ROOT=$(CDPATH= cd -- "$HERE/.." && pwd)
CLI="$PLUGIN_ROOT/scripts/auto_learn.sh"

if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -f "$CLAUDE_PLUGIN_ROOT/scripts/auto_learn.sh" ]; then
  CLI="$CLAUDE_PLUGIN_ROOT/scripts/auto_learn.sh"
fi

if [ ! -x "$CLI" ] && [ -f "$CLI" ]; then
  chmod +x "$CLI" 2>/dev/null || true
fi
if [ ! -f "$CLI" ]; then
  exit 0
fi

"$CLI" --hook --runtime "$RUNTIME" || exit 0
