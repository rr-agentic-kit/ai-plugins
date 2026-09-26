#!/usr/bin/env bash
# Create a work branch off an open release train (not hotfix/master).
#
# Usage:
#   ./scripts/branch-new.sh <branch-name> [--base release/X.Y.0] [--no-push]
#
# Base resolution when --base is omitted:
#   1 open release  → use it
#   2+ open         → interactive select (or fail if non-TTY)
#
# Flags:
#   --base <release/X.Y.0>   Explicit integration base
#   --no-push                Do not push -u to origin
#   --repo <owner/name>      Override gh/git remote repo for branch listing
#   -h, --help

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/release-branches.sh
source "${REPO_ROOT}/scripts/lib/release-branches.sh"

BASE=""
REPO=""
PUSH=1
NAME=""

usage() {
  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
}

die() {
  _release_die "$@"
}

emit() {
  printf '%s\n' "$@"
}

main() {
  local -a positional=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h | --help)
        usage
        exit 0
        ;;
      --base)
        [[ $# -ge 2 ]] || die "--base requires a value"
        BASE="$2"
        shift 2
        ;;
      --no-push)
        PUSH=0
        shift
        ;;
      --repo)
        [[ $# -ge 2 ]] || die "--repo requires a value"
        REPO="$2"
        shift 2
        ;;
      -*)
        die "unknown flag: $1"
        ;;
      *)
        positional+=("$1")
        shift
        ;;
    esac
  done

  [[ ${#positional[@]} -eq 1 ]] || {
    usage
    exit 2
  }
  NAME="${positional[0]}"

  case "${NAME}" in
    release/* | hotfix/* | master | main)
      die "refusing reserved branch name: ${NAME}"
      ;;
  esac
  [[ "${NAME}" != *" "* ]] || die "branch name must not contain spaces"

  command -v gh >/dev/null 2>&1 || die "gh not found on PATH"
  cd "${REPO_ROOT}"

  local base
  base="$(pick_release_branch "${BASE}")"

  git fetch origin "${base}"
  if git show-ref --verify --quiet "refs/heads/${NAME}"; then
    die "local branch already exists: ${NAME}"
  fi
  if git ls-remote --exit-code --heads origin "${NAME}" >/dev/null 2>&1; then
    die "remote branch already exists: origin/${NAME}"
  fi

  git checkout --no-track -b "${NAME}" "origin/${base}"
  emit "status=created" "branch=${NAME}" "base=${base}"

  if [[ "${PUSH}" -eq 1 ]]; then
    git push -u origin "${NAME}"
    emit "pushed=origin/${NAME}"
  else
    emit "pushed=false"
  fi
}

main "$@"
