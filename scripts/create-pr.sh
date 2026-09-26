#!/usr/bin/env bash
# Open or update a PR into an open release train (work → release/*).
#
# Usage:
#   ./scripts/create-pr.sh --title "..." --description "..."
#   ./scripts/create-pr.sh --title "..." --description "..." --base release/0.1.0
#   ./scripts/create-pr.sh --title "..." --body-file path.md
#
# Base resolution when --base is omitted: sole open release, else select.
# If a PR already exists for the head branch, updates title/body/base (no second PR).
#
# Flags:
#   --title <text>             Required
#   --description <text>       PR body (alias: --body)
#   --body-file <path>         PR body from file (overrides --description)
#   --base <release/X.Y.0>     Integration base
#   --head <branch>            Head branch (default: current)
#   --draft                    Create as draft (ignored on update)
#   --repo <owner/name>        Override gh repo
#   -h, --help

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/release-branches.sh
source "${REPO_ROOT}/scripts/lib/release-branches.sh"

TITLE=""
DESCRIPTION=""
BODY_FILE=""
BASE=""
HEAD=""
REPO=""
DRAFT=0

usage() {
  sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
}

die() {
  _release_die "$@"
}

emit() {
  printf '%s\n' "$@"
}

main() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h | --help)
        usage
        exit 0
        ;;
      --title)
        [[ $# -ge 2 ]] || die "--title requires a value"
        TITLE="$2"
        shift 2
        ;;
      --description | --body)
        [[ $# -ge 2 ]] || die "$1 requires a value"
        DESCRIPTION="$2"
        shift 2
        ;;
      --body-file)
        [[ $# -ge 2 ]] || die "--body-file requires a value"
        BODY_FILE="$2"
        shift 2
        ;;
      --base)
        [[ $# -ge 2 ]] || die "--base requires a value"
        BASE="$2"
        shift 2
        ;;
      --head)
        [[ $# -ge 2 ]] || die "--head requires a value"
        HEAD="$2"
        shift 2
        ;;
      --draft)
        DRAFT=1
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
        die "unexpected argument: $1 (see --help)"
        ;;
    esac
  done

  [[ -n "${TITLE}" ]] || die "--title is required"
  if [[ -n "${BODY_FILE}" ]]; then
    [[ -f "${BODY_FILE}" ]] || die "body file not found: ${BODY_FILE}"
  elif [[ -z "${DESCRIPTION}" ]]; then
    die "--description or --body-file is required"
  fi

  command -v gh >/dev/null 2>&1 || die "gh not found on PATH"
  cd "${REPO_ROOT}"

  if [[ -z "${HEAD}" ]]; then
    HEAD="$(git rev-parse --abbrev-ref HEAD)"
  fi
  case "${HEAD}" in
    HEAD | master | main | release/* | hotfix/*)
      die "refusing PR head: ${HEAD}"
      ;;
  esac

  local base
  base="$(pick_release_branch "${BASE}")"

  # Ensure remote head exists
  if ! git ls-remote --exit-code --heads origin "${HEAD}" >/dev/null 2>&1; then
    git push -u origin "HEAD:refs/heads/${HEAD}"
  fi

  local existing_url existing_num
  existing_url="$(_release_gh pr list --head "${HEAD}" --json url,number --jq '.[0].url // empty')"
  existing_num="$(_release_gh pr list --head "${HEAD}" --json number --jq '.[0].number // empty')"

  local -a body_args=()
  if [[ -n "${BODY_FILE}" ]]; then
    body_args=(--body-file "${BODY_FILE}")
  else
    body_args=(--body "${DESCRIPTION}")
  fi

  if [[ -n "${existing_num}" ]]; then
    _release_gh pr edit "${existing_num}" --title "${TITLE}" "${body_args[@]}" --base "${base}"
    emit "status=updated" "url=${existing_url}" "base=${base}" "head=${HEAD}"
    printf '%s\n' "${existing_url}"
    return 0
  fi

  local -a create_args=(
    pr create
    --title "${TITLE}"
    --base "${base}"
    --head "${HEAD}"
    "${body_args[@]}"
  )
  if [[ "${DRAFT}" -eq 1 ]]; then
    create_args+=(--draft)
  fi

  local url
  url="$(_release_gh "${create_args[@]}")"
  emit "status=created" "url=${url}" "base=${base}" "head=${HEAD}"
  printf '%s\n' "${url}"
}

main "$@"
