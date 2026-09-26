#!/usr/bin/env bash
# Squash a feature branch onto the integration base in an isolated clone, then
# optionally force-push the single commit back to the same remote branch name.
# On --force-push, after a successful push the caller repo (CALLER_ROOT) is synced:
# rename local source branch to backup/<branch>-pre-squash-<short-hash> (if it
# exists), fetch origin, and checkout -B from origin/<output-branch>.
#
# Bitbucket-only: exits with status=skip_gitlab on GitLab hosts.
#
# Usage:
#   squash-onto-base.sh --verify-only [<source-branch>]
#   squash-onto-base.sh --force-push [<source-branch>]
#
# <source-branch> defaults to the current branch when omitted.
#
# Env (all optional):
#   BASE_BRANCH     Override base (default: auto-detect master, then main)
#   OUTPUT_BRANCH   Force-push dest (default: same as source branch)
#   COMMIT_MSG      Full squash commit message (overrides auto-derived)
#   COMMIT_SUBJECT  Subject line only; body is still the commit bullet list
#
# Flags:
#   --yes           Skip force-push [y/N] confirmation
#   --auto-cleanup  Remove temp clone without Enter prompt
#   --no-cleanup    Keep clone for debug (overrides --auto-cleanup)
#   --integrate     rebase|none — rebase onto origin/$BASE in clone before squash
#   --base <branch> Override base branch name

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  squash-onto-base.sh --verify-only [<source-branch>]
  squash-onto-base.sh --force-push [<source-branch>]

<source-branch> defaults to the current branch when omitted.

Modes:
  --verify-only   Clone, squash, tree-check; print summary; do not push
  --force-push    Re-run the same checks, then force-with-lease after confirmation;
                  sync caller repo (backup rename + checkout from origin)

Flags:
  --yes           Skip force-push confirmation
  --auto-cleanup  Remove temp clone without Enter prompt
  --no-cleanup    Keep clone for debug
  --integrate     rebase|none (default: none)
  --base <branch> Override base branch (default: auto-detect master, then main)

Env:
  BASE_BRANCH     Override base (same as --base)
  OUTPUT_BRANCH   default: <source-branch>
  COMMIT_MSG      full squash message (overrides auto-derived)
  COMMIT_SUBJECT  subject only; body remains the commit bullet list
EOF
}

# Structured stdout for agents/commands (parseable key=value block)
emit_status() {
  local status="$1"
  local error="${2:-}"
  local message="${3:-}"
  local remediation="${4:-}"
  printf 'status=%s\n' "${status}"
  [[ -n "${error}" ]] && printf 'error=%s\n' "${error}"
  [[ -n "${message}" ]] && printf 'message=%s\n' "${message}"
  [[ -n "${remediation}" ]] && printf 'remediation=%s\n' "${remediation}"
  [[ -n "${TMP_CLONE:-}" ]] && printf 'tmp_clone=%s\n' "${TMP_CLONE}"
  [[ -n "${MERGE_BASE:-}" ]] && printf 'merge_base=%s\n' "${MERGE_BASE}"
  [[ -n "${ORIGIN_BASE:-}" ]] && printf 'origin_master=%s\n' "${ORIGIN_BASE}"
  [[ -n "${ORIGIN_BRANCH_SHA:-}" ]] && printf 'origin_branch=%s\n' "${ORIGIN_BRANCH_SHA}"
  [[ -n "${BRANCH_TREE:-}" ]] && printf 'branch_tree=%s\n' "${BRANCH_TREE}"
  [[ -n "${SQUASH_TREE:-}" ]] && printf 'squash_tree=%s\n' "${SQUASH_TREE}"
  [[ -n "${TREE_MATCH:-}" ]] && printf 'tree_match=%s\n' "${TREE_MATCH}"
  [[ -n "${BACKUP_BRANCH:-}" ]] && printf 'backup_branch=%s\n' "${BACKUP_BRANCH}"
}

fail_with() {
  local status="$1"
  local error="$2"
  local message="$3"
  local remediation="$4"
  emit_status "${status}" "${error}" "${message}" "${remediation}"
  printf 'error: %s\n' "${message}" >&2
  [[ -n "${remediation}" ]] && printf '%s\n' "${remediation}" >&2
  exit 1
}

log() {
  printf '==> %s\n' "$*"
}

confirm_default_yes() {
  local prompt="$1"
  local reply=""
  printf '%s [Y/n] ' "${prompt}"
  read -r reply || true
  case "${reply}" in
    n|N|no|NO) return 1 ;;
    *) return 0 ;;
  esac
}

confirm_default_no() {
  local prompt="$1"
  local reply=""
  printf '%s [y/N] ' "${prompt}"
  read -r reply || true
  case "${reply}" in
    y|Y|yes|YES) return 0 ;;
    *) return 1 ;;
  esac
}

commits_ahead() {
  local local_ref="$1"
  local remote_ref="$2"
  git rev-list --left-right --count "${local_ref}...${remote_ref}" 2>/dev/null \
    | awk '{print $1}'
}

commits_behind() {
  local local_ref="$1"
  local remote_ref="$2"
  git rev-list --left-right --count "${local_ref}...${remote_ref}" 2>/dev/null \
    | awk '{print $2}'
}

print_ref_status() {
  local label="$1"
  local branch="$2"
  local local_sha origin_sha ahead behind local_note origin_note

  if git show-ref --verify --quiet "refs/heads/${branch}"; then
    local_sha="$(git rev-parse --short "${branch}")"
    ahead="$(commits_ahead "${branch}" "origin/${branch}" 2>/dev/null || echo 0)"
    behind="$(commits_behind "${branch}" "origin/${branch}" 2>/dev/null || echo 0)"
    if [[ "${ahead}" -eq 0 && "${behind}" -eq 0 ]]; then
      local_note="up to date"
    elif [[ "${ahead}" -gt 0 && "${behind}" -gt 0 ]]; then
      local_note="(${ahead} ahead, ${behind} behind — diverged)"
    elif [[ "${ahead}" -gt 0 ]]; then
      local_note="(${ahead} commit$( [[ "${ahead}" -ne 1 ]] && printf 's') ahead)"
    else
      local_note="(${behind} commit$( [[ "${behind}" -ne 1 ]] && printf 's') behind)"
    fi
  else
    local_sha="(no local branch)"
    local_note=""
  fi

  if git show-ref --verify --quiet "refs/remotes/origin/${branch}"; then
    origin_sha="$(git rev-parse --short "origin/${branch}")"
    origin_note="(fetched)"
  else
    origin_sha="(not on origin)"
    origin_note=""
  fi

  printf '  %s   %s\n' "${label}" "${branch}"
  printf '    local   %s  %s\n' "${local_sha}" "${local_note}"
  printf '    origin  %s  %s\n' "${origin_sha}" "${origin_note}"
}

detect_platform() {
  local url_lower
  url_lower="$(printf '%s' "${REMOTE_URL}" | tr '[:upper:]' '[:lower:]')"
  if [[ "${url_lower}" == *"gitlab"* ]]; then
    return 1
  fi
  if [[ "${url_lower}" == *"bitbucket"* ]]; then
    return 0
  fi
  return 2
}

auto_detect_base() {
  if [[ -n "${BASE_BRANCH:-}" ]]; then
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

ensure_refs_current() {
  local source_ok=0 base_ok=0
  local -a unresolved=()
  local ahead behind prev_branch

  log "Preflight: checking refs against origin"
  git fetch origin "${BASE_BRANCH}" "${SOURCE_BRANCH}" 2>/dev/null \
    || git fetch origin "${BASE_BRANCH}" 2>/dev/null || true

  if ! git show-ref --verify --quiet "refs/remotes/origin/${SOURCE_BRANCH}"; then
    if git show-ref --verify --quiet "refs/heads/${SOURCE_BRANCH}"; then
      printf '\n!  origin/%s does not exist on the remote.\n' "${SOURCE_BRANCH}" >&2
      if confirm_default_yes "Push ${SOURCE_BRANCH} to origin with upstream?"; then
        git push -u origin "${SOURCE_BRANCH}"
        git fetch origin "${SOURCE_BRANCH}"
      else
        unresolved+=("origin/${SOURCE_BRANCH} does not exist (push was declined)")
      fi
    else
      fail_with "error" "branch_not_found" \
        "branch ${SOURCE_BRANCH} not found locally or on origin" \
        "Create or checkout the branch, or pass the branch name explicitly."
    fi
  fi

  printf '\n'
  print_ref_status "source" "${SOURCE_BRANCH}"
  printf '\n'
  print_ref_status "base" "${BASE_BRANCH}"
  printf '\n'
  printf 'The isolated clone squashes onto origin/%s and reads your branch from\n' "${BASE_BRANCH}"
  printf 'origin/%s. Both must be current before continuing.\n\n' "${SOURCE_BRANCH}"

  if git show-ref --verify --quiet "refs/heads/${SOURCE_BRANCH}"; then
    ahead="$(commits_ahead "${SOURCE_BRANCH}" "origin/${SOURCE_BRANCH}")"
    behind="$(commits_behind "${SOURCE_BRANCH}" "origin/${SOURCE_BRANCH}")"

    if [[ "${ahead}" -gt 0 && "${behind}" -gt 0 ]]; then
      fail_with "diverged" "diverged" \
        "Local ${SOURCE_BRANCH} has diverged from origin (${ahead} ahead, ${behind} behind)" \
        "Resolve manually: git pull --rebase origin ${SOURCE_BRANCH} (or push/reset as appropriate), then re-run."
    elif [[ "${ahead}" -gt 0 ]]; then
      printf '!  Local %s is %s commit(s) ahead of origin.\n' "${SOURCE_BRANCH}" "${ahead}" >&2
      printf '   The clone cannot see unpushed commits.\n\n' >&2
      if confirm_default_yes "Push ${SOURCE_BRANCH} to origin?"; then
        git push origin "${SOURCE_BRANCH}"
        git fetch origin "${SOURCE_BRANCH}"
      else
        unresolved+=("origin/${SOURCE_BRANCH} is missing ${ahead} local commit(s) (push was declined)")
      fi
    elif [[ "${behind}" -gt 0 ]]; then
      printf '  Local %s is %s commit(s) behind origin (origin has everything needed).\n\n' \
        "${SOURCE_BRANCH}" "${behind}"
    fi
  fi

  if ! git show-ref --verify --quiet "refs/heads/${BASE_BRANCH}"; then
    if git show-ref --verify --quiet "refs/remotes/origin/${BASE_BRANCH}"; then
      log "creating local ${BASE_BRANCH} tracking origin/${BASE_BRANCH}"
      git branch "${BASE_BRANCH}" "origin/${BASE_BRANCH}"
    else
      fail_with "error" "base_not_found" \
        "origin/${BASE_BRANCH} not found" \
        "Ensure the base branch exists on origin, or pass --base with a valid branch name."
    fi
  fi

  behind="$(commits_behind "${BASE_BRANCH}" "origin/${BASE_BRANCH}")"
  if [[ "${behind}" -gt 0 ]]; then
    printf '!  Local %s is %s commit(s) behind origin/%s.\n' \
      "${BASE_BRANCH}" "${behind}" "${BASE_BRANCH}" >&2
    printf '   Update local %s before continuing.\n\n' "${BASE_BRANCH}" >&2
    if confirm_default_yes "Fast-forward local ${BASE_BRANCH} from origin/${BASE_BRANCH}?"; then
      prev_branch="$(git branch --show-current)"
      git checkout "${BASE_BRANCH}"
      git merge --ff-only "origin/${BASE_BRANCH}"
      if [[ -n "${prev_branch}" ]]; then
        git checkout "${prev_branch}"
      fi
    else
      unresolved+=("local ${BASE_BRANCH} is ${behind} commit(s) behind origin/${BASE_BRANCH} (update was declined)")
    fi
  fi

  git fetch origin "${BASE_BRANCH}" "${SOURCE_BRANCH}"

  if git show-ref --verify --quiet "refs/heads/${SOURCE_BRANCH}" \
    && [[ "$(git rev-parse "${SOURCE_BRANCH}")" == "$(git rev-parse "origin/${SOURCE_BRANCH}")" ]]; then
    source_ok=1
  elif ! git show-ref --verify --quiet "refs/heads/${SOURCE_BRANCH}"; then
    source_ok=1
  fi

  if [[ "$(git rev-parse "${BASE_BRANCH}")" == "$(git rev-parse "origin/${BASE_BRANCH}")" ]]; then
    base_ok=1
  fi

  if [[ "${source_ok}" -eq 1 && "${base_ok}" -eq 1 ]]; then
    return 0
  fi

  local remediation=""
  if [[ "${source_ok}" -eq 0 ]]; then
    remediation+="git push origin ${SOURCE_BRANCH}"$'\n'
  fi
  if [[ "${base_ok}" -eq 0 ]]; then
    prev_branch="$(git branch --show-current 2>/dev/null || true)"
    if [[ -n "${prev_branch}" && "${prev_branch}" != "${BASE_BRANCH}" ]]; then
      remediation+="git checkout ${BASE_BRANCH} && git merge --ff-only origin/${BASE_BRANCH} && git checkout ${prev_branch}"$'\n'
    else
      remediation+="git checkout ${BASE_BRANCH} && git merge --ff-only origin/${BASE_BRANCH}"$'\n'
    fi
  fi
  remediation+="Then re-run: squash-onto-base.sh --verify-only"

  fail_with "error" "refs_not_current" \
    "Cannot continue — refs are not up to date" \
    "${remediation}"
}

remove_tmp_clone() {
  if [[ -n "${TMP_CLONE:-}" && -e "${TMP_CLONE}" ]]; then
    rm -rf "${TMP_CLONE}"
    log "temp clone removed: ${TMP_CLONE}"
  fi
}

prompt_remove_tmp_clone() {
  if [[ "${NO_CLEANUP}" == "true" ]]; then
    printf '\nTemp clone kept for inspection: %s\n' "${TMP_CLONE}"
    return 0
  fi
  if [[ "${AUTO_CLEANUP}" == "true" ]]; then
    remove_tmp_clone
    return 0
  fi
  printf '\nTemp clone: %s\n' "${TMP_CLONE}"
  printf 'Inspect or copy the path above. Press Enter to remove the temp clone... '
  read -r _ || true
  remove_tmp_clone
}

# Operates on CALLER_ROOT while the script cwd is TMP_CLONE.
sync_caller_after_push() {
  local short_hash backup_name suffix=0 remediation
  local -a caller_git

  if [[ "${TREE_MATCH}" != "yes" ]]; then
    log "caller sync skipped (tree_match != yes)"
    BACKUP_BRANCH="none"
    return 0
  fi

  caller_git=(git -C "${CALLER_ROOT}")
  BACKUP_BRANCH="none"

  if "${caller_git[@]}" show-ref --verify --quiet "refs/heads/${SOURCE_BRANCH}"; then
    short_hash="$("${caller_git[@]}" rev-parse --short "${SOURCE_BRANCH}")"
    backup_name="backup/${SOURCE_BRANCH}-pre-squash-${short_hash}"

    while "${caller_git[@]}" show-ref --verify --quiet "refs/heads/${backup_name}"; do
      suffix=$((suffix + 1))
      backup_name="backup/${SOURCE_BRANCH}-pre-squash-${short_hash}-${suffix}"
    done

    log "caller sync: rename local ${SOURCE_BRANCH} -> ${backup_name}"
    if ! "${caller_git[@]}" branch -m "${SOURCE_BRANCH}" "${backup_name}"; then
      fail_with "error" "caller_sync_failed" \
        "failed to rename local ${SOURCE_BRANCH} to ${backup_name}" \
        "Inspect ${CALLER_ROOT}; recover with git -C \"${CALLER_ROOT}\" checkout ${SOURCE_BRANCH}."
    fi
    BACKUP_BRANCH="${backup_name}"
  else
    log "caller sync: no local ${SOURCE_BRANCH}; skip backup rename"
  fi

  log "caller sync: fetch origin ${OUTPUT_BRANCH}"
  if ! "${caller_git[@]}" fetch origin "${OUTPUT_BRANCH}"; then
    remediation=""
    if [[ "${BACKUP_BRANCH}" != "none" ]]; then
      remediation="Recover old history: git -C \"${CALLER_ROOT}\" checkout ${BACKUP_BRANCH}"$'\n'
    fi
    remediation+="Then: git -C \"${CALLER_ROOT}\" fetch origin ${OUTPUT_BRANCH} && git -C \"${CALLER_ROOT}\" checkout -B ${OUTPUT_BRANCH} origin/${OUTPUT_BRANCH}"
    fail_with "error" "caller_sync_failed" \
      "failed to fetch origin/${OUTPUT_BRANCH} in caller repo" \
      "${remediation}"
  fi

  log "caller sync: checkout -B ${OUTPUT_BRANCH} origin/${OUTPUT_BRANCH}"
  if ! "${caller_git[@]}" checkout -B "${OUTPUT_BRANCH}" "origin/${OUTPUT_BRANCH}"; then
    remediation=""
    if [[ "${BACKUP_BRANCH}" != "none" ]]; then
      remediation="Recover old history: git -C \"${CALLER_ROOT}\" checkout ${BACKUP_BRANCH}"$'\n'
    fi
    remediation+="Then: git -C \"${CALLER_ROOT}\" checkout -B ${OUTPUT_BRANCH} origin/${OUTPUT_BRANCH}"
    fail_with "error" "caller_sync_failed" \
      "failed to checkout ${OUTPUT_BRANCH} from origin in caller repo" \
      "${remediation}"
  fi

  log "caller sync complete; local ${OUTPUT_BRANCH} matches origin; backup=${BACKUP_BRANCH}"
}

MODE=""
SOURCE_BRANCH=""
AUTO_CLEANUP="false"
NO_CLEANUP="false"
SKIP_CONFIRM="false"
INTEGRATE="none"
BASE_BRANCH="${BASE_BRANCH:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --verify-only)
      [[ -z "${MODE}" ]] || fail_with "error" "invalid_args" "specify exactly one of --verify-only or --force-push" ""
      MODE="verify-only"
      shift
      ;;
    --force-push)
      [[ -z "${MODE}" ]] || fail_with "error" "invalid_args" "specify exactly one of --verify-only or --force-push" ""
      MODE="force-push"
      shift
      ;;
    --yes)
      SKIP_CONFIRM="true"
      shift
      ;;
    --auto-cleanup)
      AUTO_CLEANUP="true"
      shift
      ;;
    --no-cleanup)
      NO_CLEANUP="true"
      shift
      ;;
    --integrate)
      [[ $# -lt 2 ]] && fail_with "error" "invalid_args" "--integrate requires rebase|none" ""
      INTEGRATE="$2"
      [[ "${INTEGRATE}" == "rebase" || "${INTEGRATE}" == "none" ]] \
        || fail_with "error" "invalid_args" "--integrate must be rebase or none" ""
      shift 2
      ;;
    --base)
      [[ $# -lt 2 ]] && fail_with "error" "invalid_args" "--base requires a branch name" ""
      BASE_BRANCH="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      fail_with "error" "invalid_args" "unknown option: $1" "$(usage)"
      ;;
    *)
      if [[ -z "${SOURCE_BRANCH}" ]]; then
        SOURCE_BRANCH="$1"
        shift
      else
        fail_with "error" "invalid_args" "unexpected argument: $1" ""
      fi
      ;;
  esac
done

[[ -n "${MODE}" ]] || fail_with "error" "invalid_args" "specify --verify-only or --force-push" "$(usage)"

SOURCE_BRANCH="${SOURCE_BRANCH:-$(git branch --show-current)}"
[[ -n "${SOURCE_BRANCH}" ]] || fail_with "error" "no_branch" "not on a branch; pass <source-branch> explicitly" ""

CALLER_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" \
  || fail_with "error" "not_git_repo" "not inside a git repository" ""

cd "${CALLER_ROOT}"

if ! git diff --quiet || ! git diff --cached --quiet; then
  fail_with "error" "dirty_tree" \
    "calling repo has uncommitted changes to tracked files" \
    "Commit or stash changes, then re-run."
fi

REMOTE_URL="$(git remote get-url origin 2>/dev/null)" \
  || fail_with "error" "no_origin" "no 'origin' remote in ${CALLER_ROOT}" ""

# Platform gate — Bitbucket only
if ! detect_platform; then
  platform_rc=$?
  if [[ "${platform_rc}" -eq 1 ]]; then
    emit_status "skip_gitlab" "skip_gitlab" \
      "GitLab hosting detected — use native MR squash merge (--squash-before-merge)" \
      "Do not run this workflow on GitLab. Use native MR squash merge (--squash-before-merge)."
    printf 'GitLab detected (%s). Use native squash merge instead.\n' "${REMOTE_URL}" >&2
    exit 0
  fi
  fail_with "error" "ambiguous_host" \
    "Cannot determine hosting platform from origin URL: ${REMOTE_URL}" \
    "Confirm this is a Bitbucket repo before running. GitLab repos should use native squash merge."
fi

# Auto-detect base branch
git fetch origin 2>/dev/null || true
if ! auto_detect_base; then
  fail_with "error" "no_base_branch" \
    "Could not auto-detect base branch (no origin/master or origin/main)" \
    "Pass --base <branch> or set BASE_BRANCH env var."
fi

OUTPUT_BRANCH="${OUTPUT_BRANCH:-${SOURCE_BRANCH}}"
COMMIT_MSG="${COMMIT_MSG:-}"
COMMIT_SUBJECT="${COMMIT_SUBJECT:-}"

if [[ "${SOURCE_BRANCH}" == "${BASE_BRANCH}" ]]; then
  fail_with "error" "same_branch" \
    "source branch (${SOURCE_BRANCH}) must differ from base branch (${BASE_BRANCH})" ""
fi

REPO_NAME="$(basename "${CALLER_ROOT}")"
TMP_CLONE="/tmp/${REPO_NAME}-squash-$$"

if [[ -e "${TMP_CLONE}" ]]; then
  fail_with "error" "tmp_exists" "temp path already exists: ${TMP_CLONE}" "Remove or rename the existing path, then re-run."
fi

# trap for auto-cleanup on unexpected exit when AUTO_CLEANUP is set
cleanup_on_exit() {
  if [[ "${AUTO_CLEANUP}" == "true" && "${NO_CLEANUP}" != "true" ]]; then
    remove_tmp_clone
  fi
}
trap cleanup_on_exit EXIT

ensure_refs_current

log "preflight ok (refs current, tracked tree clean)"
log "origin: ${REMOTE_URL}"
log "mode: ${MODE}"
log "source: ${SOURCE_BRANCH}  base: ${BASE_BRANCH}  output: ${OUTPUT_BRANCH}"
log "integrate: ${INTEGRATE}"
log "clone: ${TMP_CLONE}"

git clone "${REMOTE_URL}" "${TMP_CLONE}"
cd "${TMP_CLONE}"

log "fetch origin ${BASE_BRANCH} ${SOURCE_BRANCH}"
git fetch origin "${BASE_BRANCH}" "${SOURCE_BRANCH}"

git show-ref --verify --quiet "refs/remotes/origin/${BASE_BRANCH}" \
  || fail_with "error" "base_not_found" "origin/${BASE_BRANCH} not found in clone" ""
git show-ref --verify --quiet "refs/remotes/origin/${SOURCE_BRANCH}" \
  || fail_with "error" "branch_not_found" "origin/${SOURCE_BRANCH} not found in clone" ""

ORIGIN_BASE="$(git rev-parse "origin/${BASE_BRANCH}")"
ORIGIN_BRANCH_SHA="$(git rev-parse "origin/${SOURCE_BRANCH}")"
MERGE_BASE="$(git merge-base "origin/${BASE_BRANCH}" "origin/${SOURCE_BRANCH}")"
BRANCH_TREE="$(git rev-parse "origin/${SOURCE_BRANCH}^{tree}")"

# Classify: behind master (state C)
master_commits_not_in_branch="$(git rev-list --count "origin/${SOURCE_BRANCH}..origin/${BASE_BRANCH}" 2>/dev/null || echo 0)"
if [[ "${master_commits_not_in_branch}" -gt 0 && "${INTEGRATE}" == "none" ]]; then
  fail_with "behind_master" "behind_master" \
    "origin/${BASE_BRANCH} has ${master_commits_not_in_branch} commit(s) not reachable from origin/${SOURCE_BRANCH}" \
    "Re-run with --integrate rebase, or merge origin/${BASE_BRANCH} locally, push, then re-run.$(printf '\n')Example: squash-onto-base.sh --verify-only --integrate rebase ${SOURCE_BRANCH}"
fi

SOURCE_REF="origin/${SOURCE_BRANCH}"

if [[ "${INTEGRATE}" == "rebase" ]]; then
  log "checkout rebase-work from origin/${SOURCE_BRANCH}"
  git checkout --no-track -b rebase-work "origin/${SOURCE_BRANCH}"
  log "rebase onto origin/${BASE_BRANCH}"
  if ! git rebase "origin/${BASE_BRANCH}"; then
    fail_with "error" "rebase_failed" \
      "Rebase onto origin/${BASE_BRANCH} failed (conflicts?)" \
      "Resolve conflicts in clone at ${TMP_CLONE}, or integrate master locally first."
  fi
  SOURCE_REF="rebase-work"
fi

build_commit_message() {
  local ticket rest summary subject body line
  local -a subjects=()

  while IFS= read -r line; do
    [[ -n "${line}" ]] || continue
    subjects+=("${line}")
  done < <(git log --reverse --no-merges --format='%s' \
    "origin/${BASE_BRANCH}..${SOURCE_REF}")

  if [[ ${#subjects[@]} -eq 0 ]]; then
    fail_with "error" "no_commits" \
      "no non-merge commits on ${SOURCE_REF} relative to origin/${BASE_BRANCH}" ""
  fi

  if [[ -n "${COMMIT_MSG}" ]]; then
    printf '%s\n' "${COMMIT_MSG}"
    return
  fi

  ticket="$(printf '%s\n' "${SOURCE_BRANCH}" | grep -oE '[A-Z]{2,}-[0-9]+' | head -1 || true)"
  if [[ -n "${COMMIT_SUBJECT}" ]]; then
    subject="${COMMIT_SUBJECT}"
  elif [[ -n "${ticket}" ]]; then
    rest="${SOURCE_BRANCH#*"${ticket}"}"
    rest="${rest#/}"
    rest="${rest#-}"
    if [[ -n "${rest}" ]]; then
      summary="$(printf '%s' "${rest}" | tr '[:lower:]-' '[:upper:]_')"
      subject="${ticket} - ${summary}"
    else
      subject="${ticket} - squash onto ${BASE_BRANCH}"
    fi
  else
    subject="Squash ${SOURCE_BRANCH} onto ${BASE_BRANCH}"
  fi

  body=""
  for line in "${subjects[@]}"; do
    body+="- ${line}"$'\n'
  done

  printf '%s\n\n%s' "${subject}" "${body}"
}

log "checkout squash-work from origin/${BASE_BRANCH}"
git checkout --no-track -b squash-work "origin/${BASE_BRANCH}"

log "merge --squash ${SOURCE_REF}"
git -c merge.ff=true merge --squash "${SOURCE_REF}"

MSG="$(build_commit_message)"
log "commit squashed tree"
git commit -m "${MSG}"

SQUASH_COMMIT="$(git rev-parse HEAD)"
AHEAD="$(git rev-list --count "origin/${BASE_BRANCH}..HEAD")"
SQUASH_TREE="$(git rev-parse "HEAD^{tree}")"

log "tree equivalence verify"
if [[ "${BRANCH_TREE}" != "${SQUASH_TREE}" ]]; then
  TREE_MATCH="no"
  printf '\n    tree mismatch:\n' >&2
  printf '    origin/%s tree: %s\n' "${SOURCE_BRANCH}" "${BRANCH_TREE}" >&2
  printf '    squashed HEAD tree: %s\n' "${SQUASH_TREE}" >&2
  git diff --stat "origin/${SOURCE_BRANCH}" HEAD >&2 || true
  fail_with "tree_mismatch" "tree_mismatch" \
    "Squashed tree does not match origin/${SOURCE_BRANCH} tree" \
    "Branch tip tree differs from squashed result. Integrate origin/${BASE_BRANCH} (--integrate rebase), fix conflicts, push, re-run. Clone left at ${TMP_CLONE}"
fi

TREE_MATCH="yes"
DIFF_STAT="$(git diff --stat "origin/${SOURCE_BRANCH}" HEAD 2>/dev/null || true)"
if [[ -n "${DIFF_STAT}" && "${DIFF_STAT}" != *"0 files changed"* ]]; then
  printf '    note: secondary diff --stat (should be empty):\n%s\n' "${DIFF_STAT}" >&2
fi

if [[ "${AHEAD}" != "1" ]]; then
  fail_with "error" "wrong_commit_count" \
    "expected exactly 1 commit on top of origin/${BASE_BRANCH}, found ${AHEAD}" ""
fi

print_summary() {
  cat <<EOF

-------- squash summary --------
mode:           ${MODE}
source branch:  ${SOURCE_BRANCH}
base branch:    ${BASE_BRANCH}
output branch:  ${OUTPUT_BRANCH}
integrate:      ${INTEGRATE}
squash commit:  ${SQUASH_COMMIT}
commits ahead:  ${AHEAD} (on origin/${BASE_BRANCH})
tree match:     ${TREE_MATCH}
temp clone:     ${TMP_CLONE}
--------------------------------
EOF
}

print_summary

printf 'status=ok\n'
printf 'tree_match=%s\n' "${TREE_MATCH}"
printf 'squash_commit=%s\n' "${SQUASH_COMMIT}"
printf 'merge_base=%s\n' "${MERGE_BASE}"
printf 'origin_master=%s\n' "${ORIGIN_BASE}"
printf 'origin_branch=%s\n' "${ORIGIN_BRANCH_SHA}"
printf 'branch_tree=%s\n' "${BRANCH_TREE}"
printf 'squash_tree=%s\n' "${SQUASH_TREE}"
printf 'tmp_clone=%s\n' "${TMP_CLONE}"
printf 'integrate=%s\n' "${INTEGRATE}"
printf 'base_branch=%s\n' "${BASE_BRANCH}"

if [[ "${MODE}" == "verify-only" ]]; then
  log "verify-only complete; nothing pushed"
  trap - EXIT
  prompt_remove_tmp_clone
  exit 0
fi

if [[ "${SKIP_CONFIRM}" != "true" ]]; then
  if ! confirm_default_no "Are you sure you want to force-push to origin/${OUTPUT_BRANCH}?"; then
    fail_with "error" "push_declined" \
      "force-push aborted" \
      "Clone left at ${TMP_CLONE} for inspection."
  fi
fi

log "git push --force-with-lease origin HEAD:${OUTPUT_BRANCH}"
if ! git push --force-with-lease origin "HEAD:${OUTPUT_BRANCH}"; then
  fail_with "error" "push_rejected" \
    "force-with-lease push rejected — remote may have moved" \
    "git fetch origin ${OUTPUT_BRANCH}; inspect remote state; re-run --verify-only."
fi

log "force-push complete; remote origin/${OUTPUT_BRANCH} now points at ${SQUASH_COMMIT}"

sync_caller_after_push
printf 'backup_branch=%s\n' "${BACKUP_BRANCH}"

trap - EXIT
prompt_remove_tmp_clone
exit 0
