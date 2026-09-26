#!/usr/bin/env bash
# Smoke: clean-merged-local-branches.sh --worktree-status
set -euo pipefail

SCRIPT="$(cd "$(dirname "$0")/../../../plugins/rrraw/skills/s-git/scripts" && pwd)/clean-merged-local-branches.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git -C "$TMP" init -q
git -C "$TMP" config user.email "t@example.com"
git -C "$TMP" config user.name "t"
echo a >"$TMP/a.txt"
git -C "$TMP" add a.txt
git -C "$TMP" commit -qm init
git -C "$TMP" branch -M main
git -C "$TMP" remote add origin "$TMP"
# Fake origin/main for start_merged check
git -C "$TMP" update-ref refs/remotes/origin/main HEAD

echo dirty >"$TMP/a.txt"
out="$(cd "$TMP" && bash "$SCRIPT" --worktree-status --base main)"
echo "$out" | grep -q 'status=ok'
echo "$out" | grep -q 'dirty=yes'
echo "$out" | grep -q 'start_branch=main'
echo "$out" | grep -q 'start_merged=yes'
echo "OK worktree-status dirty+merged"
