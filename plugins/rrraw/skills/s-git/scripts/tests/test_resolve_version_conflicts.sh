#!/usr/bin/env bash
# Smoke tests for resolve_version_conflicts.py
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="${SCRIPT_DIR}/../resolve_version_conflicts.py"

PASS=0
FAIL=0

assert_eq() {
  local got="$1"
  local want="$2"
  local label="$3"
  if [[ "${got}" == "${want}" ]]; then
    PASS=$((PASS + 1))
    printf 'PASS: %s\n' "${label}"
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL: %s\n  got:  %s\n  want: %s\n' "${label}" "${got}" "${want}" >&2
  fi
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  if grep -qF "${needle}" <<< "${haystack}"; then
    PASS=$((PASS + 1))
    printf 'PASS: %s\n' "${label}"
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL: %s (missing %s)\n' "${label}" "${needle}" >&2
  fi
}

assert_not_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  if grep -qF "${needle}" <<< "${haystack}"; then
    FAIL=$((FAIL + 1))
    printf 'FAIL: %s (unexpected %s)\n' "${label}" "${needle}" >&2
  else
    PASS=$((PASS + 1))
    printf 'PASS: %s\n' "${label}"
  fi
}

test_latest_unit() {
  local out
  out="$(
    SCRIPT_PATH="${SCRIPT}" python3 - <<'PY'
from pathlib import Path
import importlib.util
import os
spec = importlib.util.spec_from_file_location(
    "rvc", Path(os.environ["SCRIPT_PATH"]).resolve()
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print(mod.latest_version("0.0.4-rc-21", "0.0.5"))
print(mod.latest_version("0.0.5", "0.0.4-rc-21"))
print(mod.latest_version("0.0.4-rc-21", "0.0.4-rc-9"))
PY
  )"
  assert_eq "$(sed -n '1p' <<< "${out}")" "0.0.5" "latest prefers release over older rc"
  assert_eq "$(sed -n '2p' <<< "${out}")" "0.0.5" "latest symmetric"
  assert_eq "$(sed -n '3p' <<< "${out}")" "0.0.4-rc-21" "latest prefers higher rc"
}

test_version_only_json() {
  local tmp repo out body
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  mkdir -p "${repo}/plugins/demo/.cursor-plugin"
  (
    cd "${repo}"
    git init -b master >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test"
    cat > plugins/demo/.cursor-plugin/plugin.json <<'EOF'
{
  "name": "demo",
  "version": "0.0.4-rc-9",
  "description": "same"
}
EOF
    git add . && git commit -m base >/dev/null
    git checkout -b feature >/dev/null 2>&1
    cat > plugins/demo/.cursor-plugin/plugin.json <<'EOF'
{
  "name": "demo",
  "version": "0.0.4-rc-21",
  "description": "same"
}
EOF
    git add . && git commit -m feat >/dev/null
    git checkout master >/dev/null 2>&1
    cat > plugins/demo/.cursor-plugin/plugin.json <<'EOF'
{
  "name": "demo",
  "version": "0.0.5",
  "description": "same"
}
EOF
    git add . && git commit -m master-bump >/dev/null
    git checkout feature >/dev/null 2>&1
    git merge master --no-edit >/dev/null 2>&1 || true
  )
  out="$(python3 "${SCRIPT}" --repo "${repo}" --apply)"
  assert_contains "${out}" "status=ok" "version-only apply status"
  assert_contains "${out}" "resolved=1" "version-only resolved count"
  body="$(cat "${repo}/plugins/demo/.cursor-plugin/plugin.json")"
  assert_contains "${body}" '"version": "0.0.5"' "wrote latest version"
  assert_not_contains "${body}" '<<<<<<<' "no markers left"
  rm -rf "${tmp}"
}

test_mixed_hunk_keeps_description_conflict() {
  local tmp repo body out
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  mkdir -p "${repo}/plugins/demo/.claude-plugin"
  (
    cd "${repo}"
    git init -b master >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test"
    cat > plugins/demo/.claude-plugin/plugin.json <<'EOF'
{
  "name": "demo",
  "version": "0.0.4-rc-9",
  "description": "base"
}
EOF
    git add . && git commit -m base >/dev/null
    git checkout -b feature >/dev/null 2>&1
    cat > plugins/demo/.claude-plugin/plugin.json <<'EOF'
{
  "name": "demo",
  "version": "0.0.4-rc-21",
  "description": "feature desc"
}
EOF
    git add . && git commit -m feat >/dev/null
    git checkout master >/dev/null 2>&1
    cat > plugins/demo/.claude-plugin/plugin.json <<'EOF'
{
  "name": "demo",
  "version": "0.0.5",
  "description": "master desc"
}
EOF
    git add . && git commit -m master-bump >/dev/null
    git checkout feature >/dev/null 2>&1
    git merge master --no-edit >/dev/null 2>&1 || true
  )
  out="$(python3 "${SCRIPT}" --repo "${repo}" --apply; true)"
  # exit 2 expected when remaining conflicts
  assert_contains "${out}" "status=partial" "mixed hunk partial status"
  body="$(cat "${repo}/plugins/demo/.claude-plugin/plugin.json")"
  assert_contains "${body}" '"version": "0.0.5"' "mixed: version resolved to latest"
  assert_contains "${body}" '<<<<<<<' "mixed: description conflict kept"
  assert_contains "${body}" 'feature desc' "mixed: ours description present"
  assert_contains "${body}" 'master desc' "mixed: theirs description present"
  rm -rf "${tmp}"
}

test_pyproject_version() {
  local tmp repo body
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  mkdir -p "${repo}"
  (
    cd "${repo}"
    git init -b master >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test"
    cat > pyproject.toml <<'EOF'
[project]
name = "x"
version = "0.0.4-rc-9"
EOF
    git add . && git commit -m base >/dev/null
    git checkout -b feature >/dev/null 2>&1
    cat > pyproject.toml <<'EOF'
[project]
name = "x"
version = "0.0.4-rc-21"
EOF
    git add . && git commit -m feat >/dev/null
    git checkout master >/dev/null 2>&1
    cat > pyproject.toml <<'EOF'
[project]
name = "x"
version = "0.0.5"
EOF
    git add . && git commit -m master-bump >/dev/null
    git checkout feature >/dev/null 2>&1
    git merge master --no-edit >/dev/null 2>&1 || true
  )
  python3 "${SCRIPT}" --repo "${repo}" --apply >/dev/null
  body="$(cat "${repo}/pyproject.toml")"
  assert_contains "${body}" 'version = "0.0.5"' "pyproject latest version"
  assert_not_contains "${body}" '<<<<<<<' "pyproject clean"
  rm -rf "${tmp}"
}

test_latest_unit
test_version_only_json
test_mixed_hunk_keeps_description_conflict
test_pyproject_version

printf '\n%d passed, %d failed\n' "${PASS}" "${FAIL}"
[[ "${FAIL}" -eq 0 ]]
