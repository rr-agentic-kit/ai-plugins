#!/usr/bin/env bash
# Classify and optionally delete local branches confirmed merged into origin/$BASE.
# Requires: clean worktree. Use --checkout-base to switch to $BASE when clean and on another branch.
# Dirty-tree / merged+dirty AskQuestion orchestration: clean-local-branches.md.
#
# Usage:
#   clean-merged-local-branches.sh --plan
#   clean-merged-local-branches.sh --delete
#   clean-merged-local-branches.sh --plan --checkout-base
#   clean-merged-local-branches.sh --delete --base main
#
# Flags:
#   --plan                  Classify only; print deleted/deleted_how candidates
#   --delete                Classify then delete confirmed branches
#   --base <name>           Override base (default: master, then main)
#   --checkout-base         When clean and HEAD != $BASE, git checkout $BASE before sync
#   --skip-validation       Skip pre-flight checks and pull (fetch only; for manual testing)

set -euo pipefail

MODE=""
BASE_BRANCH="${BASE_BRANCH:-}"
SKIP_VALIDATION=0
CHECKOUT_BASE=0
REPO_ROOT=""

usage() {
  cat <<'EOF'
Usage:
  clean-merged-local-branches.sh --plan
  clean-merged-local-branches.sh --delete

Flags:
  --plan                  Classify only
  --delete                Classify and delete confirmed branches
  --base <name>           Override base branch (default: auto-detect master, then main)
  --checkout-base         Checkout $BASE when worktree is clean and HEAD is elsewhere
  --skip-validation       Skip pre-flight checks and pull (fetch only; for manual testing)

Requires a clean worktree (unless --skip-validation).
EOF
}

log() {
  printf '==> %s\n' "$*" >&2
}

fail_with() {
  local error="$1"
  local message="$2"
  local remediation="${3:-}"
  printf 'status=error\n' 
  printf 'error=%s\n' "${error}"
  [[ -n "${message}" ]] && printf 'message=%s\n' "${message}"
  [[ -n "${remediation}" ]] && printf 'remediation=%s\n' "${remediation}"
  printf 'error: %s\n' "${message}" >&2
  [[ -n "${remediation}" ]] && printf '%s\n' "${remediation}" >&2
  exit 1
}

auto_detect_base() {
  if [[ -n "${BASE_BRANCH}" ]]; then
    return 0
  fi
  if git show-ref --verify --quiet "refs/remotes/origin/master" 2>/dev/null; then
    BASE_BRANCH="master"
    return 0
  fi
  if git show-ref --verify --quiet "refs/remotes/origin/main" 2>/dev/null; then
    BASE_BRANCH="main"
    return 0
  fi
  return 1
}

is_protected_branch() {
  local branch="$1"
  [[ "${branch}" == "${BASE_BRANCH}" || "${branch}" == "master" || "${branch}" == "main" ]]
}

worktree_path_for_branch() {
  local branch="$1"
  git worktree list --porcelain 2>/dev/null | awk -v target="${branch}" '
    /^worktree / { wt = substr($0, 10) }
    /^branch refs\/heads\// {
      ref = substr($0, 20)
      if (ref == target) { print wt; exit }
    }
  '
}

branch_upstream_gone() {
  local branch="$1"
  local track
  track="$(git for-each-ref --format='%(upstream:track)' "refs/heads/${branch}" 2>/dev/null || true)"
  [[ "${track}" == "[gone]" ]]
}

has_cherry_hint() {
  local branch="$1"
  local origin_base="origin/${BASE_BRANCH}"
  local out
  out="$(git cherry -v "${origin_base}" "${branch}" 2>/dev/null || true)"
  # '-' = equivalent patch already on upstream (squash/cherry-pick hint)
  [[ -n "${out}" ]] && grep -q '^-' <<< "${out}"
}

patch_id_for_range() {
  local range="$1"
  git format-patch --stdout "${range}" 2>/dev/null | git patch-id --stable 2>/dev/null | awk '{print $1}'
}

patch_id_for_commit() {
  local commit="$1"
  git show "${commit}" 2>/dev/null | git patch-id --stable 2>/dev/null | awk '{print $1}'
}

confirm_patch_id() {
  local branch="$1"
  local origin_base="origin/${BASE_BRANCH}"
  local mb branch_pid commit_pid
  mb="$(git merge-base "${origin_base}" "${branch}" 2>/dev/null || true)"
  if [[ -z "${mb}" ]]; then
    return 1
  fi
  branch_pid="$(patch_id_for_range "${mb}..${branch}")"
  if [[ -z "${branch_pid}" ]]; then
    return 1
  fi
  while IFS= read -r commit; do
    [[ -z "${commit}" ]] && continue
    commit_pid="$(patch_id_for_commit "${commit}")"
    if [[ -n "${commit_pid}" && "${commit_pid}" == "${branch_pid}" ]]; then
      return 0
    fi
  done < <(git rev-list "${mb}..${origin_base}" 2>/dev/null || true)
  return 1
}

is_gitlab_origin() {
  local url
  url="$(git remote get-url origin 2>/dev/null || true)"
  [[ "${url}" == *gitlab* ]]
}

confirm_merged_mr() {
  local branch="$1"
  if ! command -v glab >/dev/null 2>&1; then
    return 2
  fi
  if ! is_gitlab_origin; then
    return 2
  fi
  local out
  if out="$(glab mr list --source-branch "${branch}" --merged -F json 2>/dev/null)"; then
    [[ -n "${out}" && "${out}" != "[]" ]]
    return $?
  fi
  if ! out="$(glab mr list --source-branch "${branch}" --merged 2>/dev/null)"; then
    return 2
  fi
  grep -qE '^![0-9]+' <<< "${out}"
}

classify_branch() {
  local branch="$1"
  local origin_base="origin/${BASE_BRANCH}"
  local how="" reason_unsure=""

  if is_protected_branch "${branch}"; then
    printf 'protected\n'
    return 0
  fi

  local wt_path
  wt_path="$(worktree_path_for_branch "${branch}" || true)"
  if [[ -n "${wt_path}" ]]; then
    local head_branch
    head_branch="$(git branch --show-current 2>/dev/null || true)"
    if [[ "${branch}" != "${head_branch}" ]]; then
      printf 'blocked\n'
      return 0
    fi
  fi

  if git merge-base --is-ancestor "${branch}" "${origin_base}" 2>/dev/null; then
    printf 'confirmed:ancestor\n'
    return 0
  fi

  if confirm_patch_id "${branch}"; then
    printf 'confirmed:patch-id\n'
    return 0
  fi

  local mr_rc=0
  confirm_merged_mr "${branch}" || mr_rc=$?
  if [[ "${mr_rc}" -eq 0 ]]; then
    printf 'confirmed:mr-merged\n'
    return 0
  fi

  local unsure=0
  if branch_upstream_gone "${branch}"; then
    reason_unsure="gone"
    unsure=1
  fi
  if has_cherry_hint "${branch}"; then
    reason_unsure="${reason_unsure:+$reason_unsure,}cherry-hint"
    unsure=1
  fi
  if [[ "${mr_rc}" -eq 2 && "${unsure}" -eq 1 ]]; then
    reason_unsure="${reason_unsure},no-mr-check"
  fi

  if [[ "${unsure}" -eq 1 ]]; then
    printf 'unsure:%s\n' "${reason_unsure:-unknown}"
    return 0
  fi

  printf 'kept\n'
}

delete_branch() {
  local branch="$1"
  local how="$2"
  case "${how}" in
    ancestor)
      git branch -d "${branch}"
      ;;
    patch-id|mr-merged)
      git branch -D "${branch}"
      ;;
    *)
      fail_with "invalid_how" "internal: cannot delete ${branch} with how=${how}" ""
      ;;
  esac
}

emit_results() {
  local do_delete="$1"
  local deleted_csv="" how_csv="" unsure_csv="" blocked_csv=""
  local i branch how

  if [[ "${do_delete}" -eq 1 ]]; then
    for i in "${!deleted[@]}"; do
      branch="${deleted[$i]}"
      how="${deleted_hows[$i]}"
      delete_branch "${branch}" "${how}"
    done
  fi

  if ((${#deleted[@]} > 0)); then
    deleted_csv="$(IFS=,; echo "${deleted[*]}")"
    how_csv="$(IFS=,; echo "${deleted_hows[*]}")"
  fi
  if ((${#unsure_list[@]} > 0)); then
    unsure_csv="$(IFS=,; echo "${unsure_list[*]}")"
  fi
  if ((${#blocked_list[@]} > 0)); then
    blocked_csv="$(IFS=,; echo "${blocked_list[*]}")"
  fi

  printf 'status=ok\n'
  printf 'base=%s\n' "${BASE_BRANCH}"
  [[ -n "${deleted_csv}" ]] && printf 'deleted=%s\n' "${deleted_csv}"
  [[ -n "${how_csv}" ]] && printf 'deleted_how=%s\n' "${how_csv}"
  [[ -n "${unsure_csv}" ]] && printf 'unsure=%s\n' "${unsure_csv}"
  [[ -n "${blocked_csv}" ]] && printf 'blocked=%s\n' "${blocked_csv}"
  printf 'kept_count=%s\n' "${kept_count}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plan)
      MODE="plan"
      shift
      ;;
    --delete)
      MODE="delete"
      shift
      ;;
    --base)
      [[ $# -ge 2 ]] || fail_with "usage" "missing value for --base" "$(usage)"
      BASE_BRANCH="$2"
      shift 2
      ;;
    --checkout-base)
      CHECKOUT_BASE=1
      shift
      ;;
    --skip-validation)
      SKIP_VALIDATION=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail_with "usage" "unknown argument: $1" "$(usage)"
      ;;
  esac
done

[[ -n "${MODE}" ]] || fail_with "usage" "require --plan or --delete" "$(usage)"

if ! REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  fail_with "not_repo" "not inside a git work tree" "cd to a repository root or pass -C."
fi
cd "${REPO_ROOT}"

if ! auto_detect_base; then
  fail_with "no_base" "could not detect base (no origin/master or origin/main)" "Pass --base <name>."
fi

if [[ "${SKIP_VALIDATION}" -eq 0 ]]; then
  if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
    fail_with "dirty_tree" "worktree is dirty" "Commit, stash, or discard changes before running this script."
  fi

  head_branch="$(git branch --show-current 2>/dev/null || true)"
  if [[ "${head_branch}" != "${BASE_BRANCH}" ]]; then
    if [[ "${CHECKOUT_BASE}" -eq 1 ]]; then
      log "checkout ${BASE_BRANCH}"
      git checkout "${BASE_BRANCH}"
      head_branch="${BASE_BRANCH}"
    else
      fail_with "wrong_branch" "HEAD is '${head_branch:-detached}'; must be on ${BASE_BRANCH}" \
        "git checkout ${BASE_BRANCH} or pass --checkout-base"
    fi
  fi

  if [[ -f .git/MERGE_HEAD || -d .git/rebase-merge || -d .git/rebase-apply ]]; then
    fail_with "in_progress" "merge or rebase in progress" "Finish or abort the in-progress operation."
  fi
else
  head_branch="$(git branch --show-current 2>/dev/null || true)"
fi

log "fetch origin --prune"
git fetch origin --prune

if [[ "${SKIP_VALIDATION}" -eq 0 ]]; then
  log "pull --ff-only origin ${BASE_BRANCH}"
  if ! git pull --ff-only origin "${BASE_BRANCH}"; then
    fail_with "pull_failed" "git pull --ff-only refused" "Resolve divergence on ${BASE_BRANCH} manually."
  fi
fi

declare -a deleted=()
declare -a deleted_hows=()
declare -a unsure_list=()
declare -a blocked_list=()
kept_count=0

while IFS= read -r branch; do
  [[ -z "${branch}" ]] && continue
  if [[ "${branch}" == "${head_branch}" ]]; then
  # Never delete current branch (protected by HEAD check, but skip explicitly)
    continue
  fi

  result="$(classify_branch "${branch}")"
  case "${result}" in
    protected)
      ;;
    blocked)
      blocked_list+=("${branch}")
      ;;
    confirmed:*)
      how="${result#confirmed:}"
      deleted+=("${branch}")
      deleted_hows+=("${how}")
      ;;
    unsure:*)
      tag="${result#unsure:}"
      unsure_list+=("${branch}:${tag}")
      ;;
    kept)
      kept_count=$((kept_count + 1))
      ;;
    *)
      fail_with "internal" "unknown classification for ${branch}: ${result}" ""
      ;;
  esac
done < <(git for-each-ref --format='%(refname:short)' refs/heads/)

do_delete=0
[[ "${MODE}" == "delete" ]] && do_delete=1

emit_results "${do_delete}"
