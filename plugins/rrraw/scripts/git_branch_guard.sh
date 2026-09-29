#!/bin/sh
# POSIX launcher. Execs git_branch_guard_script with any python3 found.
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export PYTHONPATH="$HERE${PYTHONPATH:+:$PYTHONPATH}"

for _py in python3 python; do
  if command -v "$_py" >/dev/null 2>&1; then
    exec "$_py" -m git_branch_guard_script "$@"
  fi
done
printf '%s\n' "git_branch_guard: no python3 interpreter found" >&2
exit 127
