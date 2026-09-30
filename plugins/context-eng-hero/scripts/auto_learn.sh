#!/bin/sh
# POSIX launcher. Resolves CPython 3.14+, then execs auto_learn_script.
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export PYTHONPATH="$HERE${PYTHONPATH:+:$PYTHONPATH}"
PKG="$HERE/auto_learn_script"

_canon() {
  _t=$1
  [ -n "$_t" ] || return 1
  [ -f "$_t" ] || [ -L "$_t" ] || return 1
  [ -x "$_t" ] || return 1
  _d=$(CDPATH= cd -- "$(dirname -- "$_t")" && pwd -P) || return 1
  printf '%s/%s\n' "$_d" "$(basename -- "$_t")"
}

_add_cand() {
  _arg=$1
  _c=$(_canon "$_arg") || return 0
  case "$_seen" in
    *"
${_c}
"*) return 0 ;;
  esac
  _seen="${_seen}
${_c}
"
  _list="${_list}${_c}
"
}

_find_parent_project() {
  _dir=$(dirname -- "$HERE")
  while [ -n "$_dir" ]; do
    if [ -f "$_dir/pyproject.toml" ]; then
      printf '%s\n' "$_dir"
      return 0
    fi
    _parent=$(dirname -- "$_dir")
    if [ "$_parent" = "$_dir" ]; then
      break
    fi
    _dir=$_parent
  done
  return 1
}

_probe_ver() {
  _py=$1
  _ver=$("$_py" -c "import sys; print('%d.%d' % (sys.version_info[0], sys.version_info[1]))" 2>/dev/null) || {
    _ver=
    return 1
  }
  _major=${_ver%%.*}
  _minor=${_ver#*.}
  _minor=${_minor%%.*}
  if [ "$_major" -gt 3 ] 2>/dev/null; then
    return 0
  fi
  if [ "$_major" -eq 3 ] 2>/dev/null && [ "$_minor" -ge 14 ] 2>/dev/null; then
    return 0
  fi
  return 1
}

_probe_pkg() {
  _py=$1
  PYTHONPATH="$HERE" "$_py" -c "import auto_learn_script" >/dev/null 2>&1
  return $?
}

_seen=
_list=
_have_uv=0
if command -v uv >/dev/null 2>&1; then
  _have_uv=1
fi

for _name in python3.14 python3.15 python3.16 python3 python; do
  _p=$(command -v "$_name" 2>/dev/null) || continue
  _add_cand "$_p"
done

_old_ifs=$IFS
IFS=:
for _dir in $PATH; do
  IFS=$_old_ifs
  [ -n "$_dir" ] || continue
  for _cand in "$_dir"/python3.1[4-9]; do
    _add_cand "$_cand"
  done
done
IFS=$_old_ifs

_root=$(_find_parent_project) || _root=
if [ -n "$_root" ] && [ -x "$_root/.venv/bin/python" ]; then
  _add_cand "$_root/.venv/bin/python"
fi

if [ "$_have_uv" -eq 1 ]; then
  _found=$(uv python find 3.14 2>/dev/null) || _found=
  if [ -n "$_found" ]; then
    _add_cand "$_found"
  fi
fi

_ready=
while IFS= read -r _py; do
  [ -n "$_py" ] || continue
  if ! _probe_ver "$_py"; then
    continue
  fi
  if _probe_pkg "$_py"; then
    _ready=$_py
    break
  fi
done <<EOF
${_list}
EOF

if [ -n "$_ready" ]; then
  exec "$_ready" -m auto_learn_script "$@"
fi

if [ "$_have_uv" -eq 1 ] && [ -n "$_root" ]; then
  exec uv run --project "$_root" python -m auto_learn_script "$@"
fi

# Fail-open for hooks: missing python → silent exit 0 when --hook present.
for _a in "$@"; do
  case "$_a" in
    --hook) exit 0 ;;
  esac
done
printf '%s\n' "auto_learn: need CPython 3.14+ with auto_learn_script on PYTHONPATH" >&2
exit 127
