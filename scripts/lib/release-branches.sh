#!/usr/bin/env bash
# Shared helpers for release/* branch discovery (sourced by branch-new / create-pr / release).
# Caller must set REPO_ROOT. Optional: REPO (owner/name for gh --repo).

# shellcheck shell=bash

_release_die() {
  printf '%s: %s\n' "${0##*/}" "$*" >&2
  exit 1
}

_release_gh() {
  if [[ -n "${REPO:-}" ]]; then
    gh --repo "${REPO}" "$@"
  else
    gh "$@"
  fi
}

# Remote release/N.N.0 heads, one per line (unsorted).
list_release_branches() {
  local lines
  lines="$(
    _release_gh api repos/{owner}/{repo}/branches --paginate \
      --jq '.[] | select(.name | test("^release/[0-9]+\\.[0-9]+\\.0$")) | .name' 2>/dev/null \
      || true
  )"
  if [[ -z "${lines}" ]]; then
    lines="$(
      git -C "${REPO_ROOT}" ls-remote --heads origin 'release/*' \
        | awk '{print $2}' \
        | sed 's#^refs/heads/##' \
        | grep -E '^release/[0-9]+\.[0-9]+\.0$' \
        || true
    )"
  fi
  printf '%s\n' "${lines}" | sed '/^$/d'
}

sorted_release_branches() {
  list_release_branches \
    | sed 's#^release/##' \
    | grep -E '^[0-9]+\.[0-9]+\.0$' \
    | sort -t. -k1,1n -k2,2n -k3,3n \
    | sed 's#^#release/#'
}

# Lowest semver among open release/N.N.0 trains.
lowest_open_release() {
  local lowest
  lowest="$(sorted_release_branches | head -n 1 || true)"
  [[ -n "${lowest}" ]] || _release_die "no open release/N.N.0 branches on remote"
  printf '%s\n' "${lowest}"
}

validate_release_branch() {
  local branch="$1"
  [[ "${branch}" == release/* ]] || _release_die "expected release/X.Y.0, got: ${branch}"
  local ver="${branch#release/}"
  [[ "${ver}" =~ ^[0-9]+\.[0-9]+\.0$ ]] || _release_die "release branch must be N.N.0, got: ${branch}"
}

# Resolve base: explicit arg, else sole open release, else interactive select.
# Usage: pick_release_branch [explicit]
pick_release_branch() {
  local explicit="${1:-}"
  if [[ -n "${explicit}" ]]; then
    validate_release_branch "${explicit}"
    printf '%s\n' "${explicit}"
    return 0
  fi

  local -a branches=()
  local line
  while IFS= read -r line; do
    [[ -n "${line}" ]] && branches+=("${line}")
  done < <(sorted_release_branches)

  if [[ ${#branches[@]} -eq 0 ]]; then
    _release_die "no open release/N.N.0 branches on remote"
  fi
  if [[ ${#branches[@]} -eq 1 ]]; then
    printf '%s\n' "${branches[0]}"
    return 0
  fi

  if [[ ! -t 0 ]]; then
    _release_die "multiple release branches open; pass --base <release/X.Y.0> (non-interactive). open: ${branches[*]}"
  fi

  printf 'Multiple release trains open. Select base:\n' >&2
  local i
  for i in "${!branches[@]}"; do
    printf '  %d) %s\n' "$((i + 1))" "${branches[$i]}" >&2
  done
  local choice
  while true; do
    printf 'Choice [1-%d]: ' "${#branches[@]}" >&2
    read -r choice
    if [[ "${choice}" =~ ^[0-9]+$ ]] \
      && ((choice >= 1 && choice <= ${#branches[@]})); then
      printf '%s\n' "${branches[$((choice - 1))]}"
      return 0
    fi
    printf 'Invalid choice.\n' >&2
  done
}
