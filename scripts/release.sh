#!/usr/bin/env bash
# Maintainer front-end for .github/workflows/release-control.yml.
# Dispatches via gh; does not bump versions locally (CI owns that).
#
# Usage:
#   ./scripts/release.sh <command> [args] [flags]
#
# Commands:
#   open [release/X.Y.0]     Set train to X.Y.0-rc1 (default: lowest open release/*)
#   rc [release/X.Y.0]       Tick RC (default: lowest open release/*)
#   promote [release/X.Y.0]  Graduate train (default: lowest open release/*)
#   hotfix <hotfix/X.Y.Z>    Ship patch version from hotfix branch name
#   next-minor [VERSION]     Print next minor train (CI helper; optional version)
#   seed <X.Y.0>             Create+push release/X.Y.0 from master, then open
#   active                   Print the lowest open release/* branch
#   watch                    Watch the latest release-control run
#   status                   Active release/* branches + recent workflow runs
#
# When a release branch is omitted, the script picks the lowest semver among
# remote heads matching release/N.N.0 (e.g. release/0.1.0 before release/0.2.0).
#
# Flags:
#   --ref <branch>           Branch whose workflow YAML to run
#                            (default: master if it has the file, else target /
#                            lowest open release/* — needed until promote lands YAML on master)
#   --repo <owner/name>      Override gh repo (default: cwd origin)
#   --yes                    Skip seed confirmation
#   -h, --help               Show this help
#
# Exemples:
# ./scripts/release.sh active   # → branch=release/0.1.0
# ./scripts/release.sh open     # opens that train
# ./scripts/release.sh rc
# ./scripts/release.sh promote
#

set -euo pipefail

WORKFLOW="release-control.yml"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF=""
REPO=""
YES=0

usage() {
  sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'
}

die() {
  printf 'release.sh: %s\n' "$*" >&2
  exit 1
}

emit() {
  printf '%s\n' "$@"
}

require_gh() {
  command -v gh >/dev/null 2>&1 || die "gh not found on PATH"
  gh auth status -h github.com >/dev/null 2>&1 || die "gh not authenticated (gh auth login)"
}

repo_flag() {
  if [[ -n "${REPO}" ]]; then
    printf -- '--repo %q' "${REPO}"
  fi
}

gh_repo() {
  # shellcheck disable=SC2046
  gh $(repo_flag) "$@"
}

default_branch() {
  local name
  name="$(gh_repo repo view --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null || true)"
  if [[ -n "${name}" ]]; then
    printf '%s\n' "${name}"
    return 0
  fi
  printf 'master\n'
}

# Remote release/N.N.0 heads, one per line (unsorted).
list_release_branches() {
  local lines
  lines="$(
    gh_repo api repos/{owner}/{repo}/branches --paginate \
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
  printf '%s\n' "${lines}"
}

# Lowest semver among open release/N.N.0 trains (e.g. 0.1.0 before 0.2.0).
lowest_open_release() {
  local lowest
  lowest="$(
    list_release_branches \
      | sed 's#^release/##' \
      | grep -E '^[0-9]+\.[0-9]+\.0$' \
      | sort -t. -k1,1n -k2,2n -k3,3n \
      | head -n 1 \
      || true
  )"
  [[ -n "${lowest}" ]] || die "no open release/N.N.0 branches on remote"
  printf 'release/%s\n' "${lowest}"
}

resolve_branch_arg() {
  local want="$1"
  local branch="${2:-}"
  if [[ -z "${branch}" ]]; then
    case "${want}" in
      release) branch="$(lowest_open_release)" ;;
      hotfix) die "hotfix branch required (e.g. hotfix/0.1.1)" ;;
    esac
  fi
  [[ -n "${branch}" ]] || die "branch required"
  case "${want}" in
    release)
      [[ "${branch}" == release/* ]] || die "expected release/X.Y.0, got: ${branch}"
      local ver="${branch#release/}"
      [[ "${ver}" =~ ^[0-9]+\.[0-9]+\.0$ ]] || die "release branch must be N.N.0, got: ${branch}"
      ;;
    hotfix)
      [[ "${branch}" == hotfix/* ]] || die "expected hotfix/X.Y.Z, got: ${branch}"
      local ver="${branch#hotfix/}"
      [[ "${ver}" =~ ^[0-9]+\.[0-9]+\.[1-9][0-9]*$ ]] || die "hotfix patch must be > 0, got: ${branch}"
      ;;
  esac
  printf '%s\n' "${branch}"
}

# gh workflow run reads the YAML from --ref (default = repo default branch).
# Until promote, release-control.yml lives on release/* only — not master.
workflow_ref_for() {
  local target="${1:-}"
  if [[ -n "${REF}" ]]; then
    printf '%s\n' "${REF}"
    return 0
  fi
  local base
  base="$(default_branch)"
  git -C "${REPO_ROOT}" fetch origin "${base}" --quiet 2>/dev/null || true
  if git -C "${REPO_ROOT}" cat-file -e "origin/${base}:.github/workflows/${WORKFLOW}" 2>/dev/null; then
    printf '%s\n' "${base}"
    return 0
  fi
  if [[ -n "${target}" ]]; then
    git -C "${REPO_ROOT}" fetch origin "${target}" --quiet 2>/dev/null || true
    if git -C "${REPO_ROOT}" cat-file -e "origin/${target}:.github/workflows/${WORKFLOW}" 2>/dev/null; then
      printf '%s\n' "${target}"
      return 0
    fi
  fi
  local lowest
  lowest="$(lowest_open_release)"
  git -C "${REPO_ROOT}" fetch origin "${lowest}" --quiet 2>/dev/null || true
  if git -C "${REPO_ROOT}" cat-file -e "origin/${lowest}:.github/workflows/${WORKFLOW}" 2>/dev/null; then
    printf '%s\n' "${lowest}"
    return 0
  fi
  die "no branch has .github/workflows/${WORKFLOW}; pass --ref <branch>"
}

dispatch() {
  local action="$1"
  local branch="${2:-}"
  local version="${3:-}"
  local run_ref
  run_ref="$(workflow_ref_for "${branch}")"
  local -a args=(workflow run "${WORKFLOW}" --ref "${run_ref}")

  args+=(-f "action=${action}")
  if [[ -n "${branch}" ]]; then
    args+=(-f "branch=${branch}")
  fi
  if [[ -n "${version}" ]]; then
    args+=(-f "version=${version}")
  fi

  # shellcheck disable=SC2046
  gh_repo "${args[@]}"
  emit "status=dispatched" "action=${action}"
  [[ -n "${branch}" ]] && emit "branch=${branch}"
  [[ -n "${version}" ]] && emit "version=${version}"
  emit "ref=${run_ref}"
  emit "hint=run: ./scripts/release.sh watch"
}

cmd_open() {
  local branch
  branch="$(resolve_branch_arg release "${1:-}")"
  dispatch open "${branch}"
}

cmd_rc() {
  local branch
  branch="$(resolve_branch_arg release "${1:-}")"
  dispatch rc "${branch}"
}

cmd_promote() {
  local branch
  branch="$(resolve_branch_arg release "${1:-}")"
  dispatch promote "${branch}"
}

cmd_hotfix() {
  local branch
  branch="$(resolve_branch_arg hotfix "${1:-}")"
  dispatch hotfix "${branch}"
}

cmd_next_minor() {
  local version="${1:-}"
  dispatch next-minor "" "${version}"
}

cmd_seed() {
  local ver="${1:-}"
  [[ -n "${ver}" ]] || die "usage: release.sh seed <X.Y.0>"
  [[ "${ver}" =~ ^[0-9]+\.[0-9]+\.0$ ]] || die "seed version must be N.N.0, got: ${ver}"

  local branch="release/${ver}"
  local base
  base="$(default_branch)"

  if gh_repo api "repos/{owner}/{repo}/branches/${branch}" --silent >/dev/null 2>&1; then
    die "branch already exists on remote: ${branch}"
  fi

  if [[ "${YES}" -ne 1 ]]; then
    printf 'Create and push %s from origin/%s, then dispatch open? [y/N] ' "${branch}" "${base}" >&2
    local ans
    read -r ans
    [[ "${ans}" == [yY] || "${ans}" == [yY][eE][sS] ]] || die "aborted"
  fi

  git -C "${REPO_ROOT}" fetch origin "${base}"
  git -C "${REPO_ROOT}" branch "${branch}" "origin/${base}" 2>/dev/null \
    || git -C "${REPO_ROOT}" branch -f "${branch}" "origin/${base}"
  git -C "${REPO_ROOT}" push -u origin "${branch}"

  # Prefer running the workflow from the new branch once it has the YAML;
  # fall back to --ref / default branch for bootstrap.
  if [[ -z "${REF}" ]]; then
    if git -C "${REPO_ROOT}" cat-file -e "origin/${branch}:.github/workflows/${WORKFLOW}" 2>/dev/null; then
      REF="${branch}"
    fi
  fi

  dispatch open "${branch}"
  emit "seeded=${branch}" "from=${base}"
}

cmd_watch() {
  local id
  id="$(gh_repo run list --workflow "${WORKFLOW}" --limit 1 --json databaseId --jq '.[0].databaseId // empty')"
  [[ -n "${id}" ]] || die "no release-control runs found"
  emit "run_id=${id}"
  gh_repo run watch "${id}" --exit-status
}

cmd_active() {
  local branch
  branch="$(lowest_open_release)"
  emit "branch=${branch}"
}

cmd_status() {
  local active=""
  active="$(lowest_open_release 2>/dev/null || true)"
  emit "=== active release branches ==="
  list_release_branches \
    | sed 's#^release/##' \
    | grep -E '^[0-9]+\.[0-9]+\.0$' \
    | sort -t. -k1,1n -k2,2n -k3,3n \
    | sed 's#^#release/#'
  if [[ -n "${active}" ]]; then
    emit "lowest=${active}"
  fi
  emit ""
  emit "=== recent release-control runs ==="
  gh_repo run list --workflow "${WORKFLOW}" --limit 8
}

main() {
  cd "${REPO_ROOT}"
  require_gh

  local -a positional=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h | --help)
        usage
        exit 0
        ;;
      --ref)
        [[ $# -ge 2 ]] || die "--ref requires a value"
        REF="$2"
        shift 2
        ;;
      --repo)
        [[ $# -ge 2 ]] || die "--repo requires a value"
        REPO="$2"
        shift 2
        ;;
      --yes)
        YES=1
        shift
        ;;
      --)
        shift
        positional+=("$@")
        break
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

  [[ ${#positional[@]} -ge 1 ]] || {
    usage
    exit 2
  }

  local cmd="${positional[0]}"
  local -a args=("${positional[@]:1}")

  case "${cmd}" in
    open) cmd_open "${args[@]:-}" ;;
    rc) cmd_rc "${args[@]:-}" ;;
    promote) cmd_promote "${args[@]:-}" ;;
    hotfix) cmd_hotfix "${args[@]:-}" ;;
    next-minor) cmd_next_minor "${args[@]:-}" ;;
    seed) cmd_seed "${args[@]:-}" ;;
    active) cmd_active ;;
    watch) cmd_watch ;;
    status) cmd_status ;;
    *)
      die "unknown command: ${cmd} (see --help)"
      ;;
  esac
}

main "$@"
