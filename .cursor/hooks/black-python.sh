#!/usr/bin/env bash
# Reformat edited Python files with Black via uv.
set -euo pipefail

input=$(cat)
file_path=$(echo "$input" | jq -r '.file_path // empty')
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0] // empty')

if [[ -z "$file_path" || "$file_path" != *.py ]]; then
  exit 0
fi

if ! command -v uv >/dev/null 2>&1; then
  exit 0
fi

if [[ -n "$workspace_root" && -d "$workspace_root" ]]; then
  cd "$workspace_root"
elif git rev-parse --show-toplevel >/dev/null 2>&1; then
  cd "$(git rev-parse --show-toplevel)"
fi

target="$file_path"
if [[ -n "$workspace_root" && "$file_path" == "$workspace_root"/* ]]; then
  target="${file_path#"$workspace_root"/}"
fi

if ! uv run black "$target" >&2; then
  echo "black-python hook: black failed for $target" >&2
fi

exit 0
