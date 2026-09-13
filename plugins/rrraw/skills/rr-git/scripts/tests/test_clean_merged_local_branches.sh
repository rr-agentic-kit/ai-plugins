#!/usr/bin/env bash
# Smoke tests for clean-merged-local-branches.sh (temp repos).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="${SCRIPT_DIR}/../clean-merged-local-branches.sh"

PASS=0
FAIL=0

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
    printf 'output:\n%s\n' "${haystack}" >&2
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

init_repo() {
  local dir="$1"
  mkdir -p "${dir}"
  (
    cd "${dir}"
    git init -b master >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test User"
    git config merge.ff true
    echo "base" > README.md
    git add README.md
    git commit -m "initial" >/dev/null
  )
}

setup_origin() {
  local repo="$1"
  local bare="$2"
  git init --bare "${bare}" >/dev/null 2>&1
  (
    cd "${repo}"
    git remote add origin "${bare}"
    git push -u origin master >/dev/null 2>&1
  )
}

test_ancestor_deleted_with_d() {
  local tmp repo bare out
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  bare="${tmp}/origin.git"
  init_repo "${repo}"
  setup_origin "${repo}" "${bare}"

  cd "${repo}"
  git checkout -b feature-merged >/dev/null 2>&1
  echo "feat" >> README.md
  git add README.md
  git commit -m "feature work" >/dev/null
  git checkout master >/dev/null 2>&1
  git merge --no-ff feature-merged -m "merge feature" >/dev/null
  git push origin master >/dev/null 2>&1
  out="$( "${SCRIPT}" --delete 2>/dev/null )"
  assert_contains "${out}" "status=ok" "ancestor: status ok"
  assert_contains "${out}" "deleted=feature-merged" "ancestor: deleted feature-merged"
  assert_contains "${out}" "deleted_how=ancestor" "ancestor: how ancestor"
  if git show-ref --verify --quiet refs/heads/feature-merged; then
    FAIL=$((FAIL + 1))
    printf 'FAIL: ancestor branch still exists\n' >&2
  else
    PASS=$((PASS + 1))
    printf 'PASS: ancestor branch removed\n'
  fi
  cd - >/dev/null
  rm -rf "${tmp}"
}

test_squash_patch_id_deleted_with_D() {
  local tmp repo bare out
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  bare="${tmp}/origin.git"
  init_repo "${repo}"
  setup_origin "${repo}" "${bare}"

  cd "${repo}"
  git checkout -b feature-squash >/dev/null 2>&1
  echo "squash me" >> README.md
  git add README.md
  git commit -m "squash work" >/dev/null
  git checkout master >/dev/null 2>&1
  git merge --squash feature-squash >/dev/null
  git commit -m "Squashed feature-squash" >/dev/null
  git push origin master >/dev/null 2>&1
  out="$( "${SCRIPT}" --delete 2>/dev/null )"
  assert_contains "${out}" "status=ok" "squash: status ok"
  assert_contains "${out}" "deleted=feature-squash" "squash: deleted feature-squash"
  assert_contains "${out}" "deleted_how=patch-id" "squash: how patch-id"
  if git show-ref --verify --quiet refs/heads/feature-squash; then
    FAIL=$((FAIL + 1))
    printf 'FAIL: squash branch still exists\n' >&2
  else
    PASS=$((PASS + 1))
    printf 'PASS: squash branch removed\n'
  fi
  cd - >/dev/null
  rm -rf "${tmp}"
}

test_unique_kept_not_deleted() {
  local tmp repo bare out
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  bare="${tmp}/origin.git"
  init_repo "${repo}"
  setup_origin "${repo}" "${bare}"

  cd "${repo}"
  git checkout -b unique-work >/dev/null 2>&1
  echo "only local" >> README.md
  git add README.md
  git commit -m "unique" >/dev/null
  git checkout master >/dev/null 2>&1
  out="$( "${SCRIPT}" --plan 2>/dev/null )"
  assert_contains "${out}" "status=ok" "kept: status ok"
  assert_not_contains "${out}" "deleted=unique-work" "kept: not in deleted"
  assert_not_contains "${out}" "unsure=unique-work" "kept: not unsure"
  if git show-ref --verify --quiet refs/heads/unique-work; then
    PASS=$((PASS + 1))
    printf 'PASS: unique branch kept\n'
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL: unique branch was deleted\n' >&2
  fi
  cd - >/dev/null
  rm -rf "${tmp}"
}

test_gone_unsure_not_deleted() {
  local tmp repo bare out
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  bare="${tmp}/origin.git"
  init_repo "${repo}"
  setup_origin "${repo}" "${bare}"

  cd "${repo}"
  git checkout -b gone-upstream >/dev/null 2>&1
  echo "gone" >> README.md
  git add README.md
  git commit -m "gone work" >/dev/null
  git push -u origin gone-upstream >/dev/null 2>&1
  git push origin --delete gone-upstream >/dev/null 2>&1
  git fetch origin --prune >/dev/null 2>&1
  git checkout master >/dev/null 2>&1
  out="$( "${SCRIPT}" --plan 2>/dev/null )"
  assert_contains "${out}" "status=ok" "gone: status ok"
  assert_contains "${out}" "unsure=gone-upstream" "gone: listed unsure"
  assert_not_contains "${out}" "deleted=gone-upstream" "gone: not deleted"
  if git show-ref --verify --quiet refs/heads/gone-upstream; then
    PASS=$((PASS + 1))
    printf 'PASS: gone branch kept\n'
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL: gone branch was deleted\n' >&2
  fi
  cd - >/dev/null
  rm -rf "${tmp}"
}

test_glab_empty_mr_list_kept_not_deleted() {
  local tmp repo bare bin out
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  bare="${tmp}/gitlab-mock/origin.git"
  bin="${tmp}/bin"
  init_repo "${repo}"
  setup_origin "${repo}" "${bare}"

  mkdir -p "${bin}"
  cat > "${bin}/glab" <<'EOF'
#!/usr/bin/env bash
if [[ "$*" == *"-F json"* ]]; then
  printf '[]\n'
  exit 0
fi
if [[ "$*" == *"--merged"* ]]; then
  printf 'No merged merge requests match your search in group/repo.\n'
  exit 0
fi
exit 1
EOF
  chmod +x "${bin}/glab"

  cd "${repo}"
  git remote set-url origin "${bare}"
  git checkout -b temp-local >/dev/null 2>&1
  echo "only local" >> README.md
  git add README.md
  git commit -m "unique local work" >/dev/null
  git checkout master >/dev/null 2>&1
  out="$( PATH="${bin}:${PATH}" "${SCRIPT}" --plan 2>/dev/null )"
  assert_contains "${out}" "status=ok" "glab empty: status ok"
  assert_not_contains "${out}" "deleted=temp-local" "glab empty: not in deleted"
  assert_not_contains "${out}" "unsure=temp-local" "glab empty: not unsure"
  if git show-ref --verify --quiet refs/heads/temp-local; then
    PASS=$((PASS + 1))
    printf 'PASS: glab empty branch kept\n'
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL: glab empty branch was deleted\n' >&2
  fi
  cd - >/dev/null
  rm -rf "${tmp}"
}

test_dirty_tree_errors() {
  local tmp repo bare out
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  bare="${tmp}/origin.git"
  init_repo "${repo}"
  setup_origin "${repo}" "${bare}"

  cd "${repo}"
  echo "dirty" >> README.md
  out="$( "${SCRIPT}" --plan 2>/dev/null || true )"
  assert_contains "${out}" "status=error" "dirty: status error"
  assert_contains "${out}" "error=dirty_tree" "dirty: dirty_tree error"
  cd - >/dev/null
  rm -rf "${tmp}"
}

test_skip_validation_allows_dirty_tree() {
  local tmp repo bare out
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  bare="${tmp}/origin.git"
  init_repo "${repo}"
  setup_origin "${repo}" "${bare}"

  cd "${repo}"
  echo "dirty" >> README.md
  out="$( "${SCRIPT}" --plan --skip-validation 2>/dev/null || true )"
  assert_contains "${out}" "status=ok" "skip validation: status ok"
  assert_not_contains "${out}" "error=dirty_tree" "skip validation: no dirty_tree error"
  cd - >/dev/null
  rm -rf "${tmp}"
}

test_wrong_branch_errors() {
  local tmp repo bare out
  tmp="$(mktemp -d)"
  repo="${tmp}/repo"
  bare="${tmp}/origin.git"
  init_repo "${repo}"
  setup_origin "${repo}" "${bare}"

  cd "${repo}"
  git checkout -b not-base >/dev/null 2>&1
  out="$( "${SCRIPT}" --plan 2>/dev/null || true )"
  assert_contains "${out}" "status=error" "wrong branch: status error"
  assert_contains "${out}" "error=wrong_branch" "wrong branch: wrong_branch error"
  cd - >/dev/null
  rm -rf "${tmp}"
}

main() {
  [[ -x "${SCRIPT}" ]] || chmod +x "${SCRIPT}"
  test_ancestor_deleted_with_d
  test_squash_patch_id_deleted_with_D
  test_unique_kept_not_deleted
  test_glab_empty_mr_list_kept_not_deleted
  test_gone_unsure_not_deleted
  test_dirty_tree_errors
  test_skip_validation_allows_dirty_tree
  test_wrong_branch_errors
  printf '\n%d passed, %d failed\n' "${PASS}" "${FAIL}"
  [[ "${FAIL}" -eq 0 ]]
}

main "$@"
