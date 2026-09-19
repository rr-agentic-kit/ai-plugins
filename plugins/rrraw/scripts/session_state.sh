#!/bin/sh
# Thin launcher for session_state_cli.py (stdlib only).
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$HERE/session_state_cli.py" "$@"
