#!/bin/sh
# List unresolved PR review threads (filtered JSON) or reply by GraphQL thread id.
# Requires: gh, jq. Query/mutation stay in this script.
#
# Usage:
#   open-review-threads.sh [--owner OWNER] [--repo REPO] [--pr NUMBER]
#   open-review-threads.sh --reply THREAD_ID (--body TEXT | --body-file PATH)

set -eu

OWNER=""
REPO=""
PR=""
REPLY=""
BODY=""
BODY_FILE=""

THREADS_QUERY='query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          path
          line
          isOutdated
          comments(first: 20) {
            nodes {
              author { login }
              body
            }
          }
        }
      }
    }
  }
}'

REPLY_MUTATION='mutation($threadId: ID!, $body: String!) {
  addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
    comment { id }
  }
}'

usage() {
  cat <<'EOF'
Usage:
  open-review-threads.sh [--owner OWNER] [--repo REPO] [--pr NUMBER]
  open-review-threads.sh --reply THREAD_ID (--body TEXT | --body-file PATH)

List (default): stdout is a JSON array of unresolved threads with id, path, line,
outdated, and comments (author, body). No url; resolved threads omitted. Empty is [].

Reply: stdout is {"thread_id","comment_id"}. Does not resolve the thread.

Exits: 0 success; 1 no open PR (list); 2 usage/flag errors.
EOF
}

die() {
  printf 'open-review-threads: %s\n' "$1" >&2
  exit "${2:-2}"
}

require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    die "jq is required" 2
  fi
}

resolve_owner_repo() {
  if [ -n "${OWNER}" ] && [ -n "${REPO}" ]; then
    return 0
  fi
  nwo="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
  OWNER="${nwo%%/*}"
  REPO="${nwo#*/}"
  if [ -z "${OWNER}" ] || [ -z "${REPO}" ] || [ "${REPO}" = "${nwo}" ]; then
    die "could not parse owner/repo from gh repo view" 2
  fi
}

check_owner_repo_pair() {
  if [ -n "${OWNER}" ] && [ -z "${REPO}" ]; then
    die "--owner requires --repo" 2
  fi
  if [ -n "${REPO}" ] && [ -z "${OWNER}" ]; then
    die "--repo requires --owner" 2
  fi
}

resolve_pr() {
  if [ -n "${PR}" ]; then
    return 0
  fi
  if ! PR="$(gh pr view --repo "${OWNER}/${REPO}" --json number -q .number 2>/dev/null)"; then
    die "no open pull request for current branch" 1
  fi
  if [ -z "${PR}" ]; then
    die "no open pull request for current branch" 1
  fi
}

list_threads() {
  require_jq
  raw="$(gh api graphql \
    -f query="${THREADS_QUERY}" \
    -f owner="${OWNER}" \
    -f name="${REPO}" \
    -F number="${PR}")"

  count="$(printf '%s' "${raw}" | jq '.data.repository.pullRequest.reviewThreads.nodes | length')"
  if [ "${count}" -eq 100 ]; then
    printf 'open-review-threads: reviewThreads truncated at 100 nodes\n' >&2
  fi

  printf '%s' "${raw}" | jq -c '
    [.data.repository.pullRequest.reviewThreads.nodes[]
      | select(.isResolved == false)
      | {
          id: .id,
          path: .path,
          line: .line,
          outdated: .isOutdated,
          comments: [.comments.nodes[] | {author: .author.login, body: .body}]
        }]
  '
}

do_reply() {
  thread_id="$1"
  body_text="$2"
  require_jq
  raw="$(gh api graphql \
    -f query="${REPLY_MUTATION}" \
    -f threadId="${thread_id}" \
    -f body="${body_text}")"
  printf '%s' "${raw}" | jq -c --arg tid "${thread_id}" \
    '{thread_id: $tid, comment_id: .data.addPullRequestReviewThreadReply.comment.id}'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --owner)
      [ $# -ge 2 ] || die "missing value for --owner" 2
      OWNER="$2"
      shift 2
      ;;
    --repo)
      [ $# -ge 2 ] || die "missing value for --repo" 2
      REPO="$2"
      shift 2
      ;;
    --pr)
      [ $# -ge 2 ] || die "missing value for --pr" 2
      PR="$2"
      shift 2
      ;;
    --reply)
      [ $# -ge 2 ] || die "missing value for --reply" 2
      REPLY="$2"
      shift 2
      ;;
    --body)
      [ $# -ge 2 ] || die "missing value for --body" 2
      BODY="$2"
      shift 2
      ;;
    --body-file)
      [ $# -ge 2 ] || die "missing value for --body-file" 2
      BODY_FILE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1" 2
      ;;
  esac
done

check_owner_repo_pair

if [ -n "${REPLY}" ]; then
  if [ -z "${BODY}" ] && [ -z "${BODY_FILE}" ]; then
    die "--reply requires --body or --body-file" 2
  fi
  if [ -n "${BODY}" ] && [ -n "${BODY_FILE}" ]; then
    die "pass only one of --body or --body-file" 2
  fi
  if [ -n "${BODY_FILE}" ]; then
    BODY="$(cat "${BODY_FILE}")"
  fi
  do_reply "${REPLY}" "${BODY}"
  exit 0
fi

resolve_owner_repo
resolve_pr
list_threads
