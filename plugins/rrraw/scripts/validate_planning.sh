#!/bin/sh
# POSIX launcher. Resolves CPython 3.14+ with PyYAML, then execs the package CLI.
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export PYTHONPATH="$HERE${PYTHONPATH:+:$PYTHONPATH}"
PKG="$HERE/validate_planning_script"

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

_probe_yaml() {
  _py=$1
  PYTHONPATH="$HERE" "$_py" -c "import yaml, validate_planning_script" >/dev/null 2>&1
  return $?
}

_probe_ok() {
  PYTHONPATH="$HERE" "$@" -c "import sys, yaml, validate_planning_script; raise SystemExit(0 if sys.version_info >= (3, 14) else 1)" >/dev/null 2>&1
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
_old_py=
_old_ver=
_no_yaml_py=
_have_314=0

while IFS= read -r _py; do
  [ -n "$_py" ] || continue
  if ! _probe_ver "$_py"; then
    if [ -z "$_old_py" ] && [ -n "$_ver" ]; then
      _old_py=$_py
      _old_ver=$_ver
    fi
    continue
  fi
  _have_314=1
  if _probe_yaml "$_py"; then
    _ready=$_py
    break
  fi
  if [ -z "$_no_yaml_py" ]; then
    _no_yaml_py=$_py
  fi
done <<EOF
${_list}
EOF

if [ -n "$_ready" ]; then
  exec "$_ready" -m validate_planning_script "$@"
fi

if [ "$_have_uv" -eq 1 ]; then
  if [ -n "$_root" ] && _probe_ok uv run --project "$_root" python; then
    exec uv run --project "$_root" python -m validate_planning_script "$@"
  fi
  if [ -z "$_root" ] && [ -f "$PKG/pyproject.toml" ] && _probe_ok uv run --project "$PKG" python; then
    exec uv run --project "$PKG" python -m validate_planning_script "$@"
  fi
  if _probe_ok uv run --no-project --python 3.14 --with 'pyyaml>=6.0.3' python; then
    exec uv run --no-project --python 3.14 --with 'pyyaml>=6.0.3' python -m validate_planning_script "$@"
  fi
fi

if [ -z "$_old_py" ] && [ "$_have_314" -eq 0 ] && [ -z "$_no_yaml_py" ]; then
  printf '%s\n' "no Python interpreter found (tried python3.14, python3, python, uv)" >&2
  exit 127
fi
if [ "$_have_314" -eq 0 ] && [ -n "$_old_py" ]; then
  printf '%s\n' "found Python ${_old_ver}.x at ${_old_py}; need CPython 3.14+" >&2
  exit 127
fi
if [ -n "$_no_yaml_py" ]; then
  printf '%s\n' "${_no_yaml_py} -m pip install -r scripts/validate_planning_script/requirements.txt" >&2
  exit 127
fi
printf '%s\n' "no Python interpreter found (tried python3.14, python3, python, uv)" >&2
exit 127
