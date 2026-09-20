# GitLab MCP Workflow Patterns

Wiring that is **not** in MCP tool schemas. Policy for inline vs general notes and `+`-line anchors: [inline-comments.md](inline-comments.md). Pipeline `reports:codequality`: **glab** GraphQL via [code-quality-reports.md](code-quality-reports.md)—not available through MCP.

## Get user IDs for assignment

MCP `assignee_ids` / `reviewer_ids` take **numeric IDs**, not usernames.

- **Current user:** `whoami` → use `.id`.
- **Other users:** `list_project_members` (or glab) and take `.id`. Do **not** call `get_users` (not in this MCP). `get_user` requires `user_id` already.

```typescript
const me = whoami()
update_merge_request({
  merge_request_iid: "123",
  assignee_ids: [me.id],
})
```

## Create code comment

Run CLI `mr-inline-anchors` for `diff_refs` + `files[path]` (`+` lines). Do **not** invent unified-diff parse in the agent. Then `create_merge_request_thread` with `new_line` chosen from that set and the same `position` rules as [inline-comments.md](inline-comments.md).

```typescript
// Prefer: rr-ci mr-inline-anchors → result.diff_refs + result.files[path]
const anchors = /* parse CLI envelope */
create_merge_request_thread({
  merge_request_iid: "123",
  body: "Add error handling here",
  position: {
    position_type: "text",
    base_sha: anchors.diff_refs.base_sha,
    head_sha: anchors.diff_refs.head_sha,
    start_sha: anchors.diff_refs.start_sha,
    new_path: "src/auth.ts",
    old_path: "src/auth.ts",
    new_line: anchors.files["src/auth.ts"][0], // must be in files[path]
  },
})
```

## Reviewer assignment with MR comments

Posting review feedback implies the user is **reviewing**. Merge **existing** `reviewer_ids` with **`whoami().id`**. Passing only the new ID **replaces** the list.

```typescript
const mr = get_merge_request({ merge_request_iid: "123" })
const myId = whoami().id
const existingIds = (mr.reviewers ?? []).map((r) => r.id)
if (!existingIds.includes(myId)) {
  update_merge_request({
    merge_request_iid: "123",
    reviewer_ids: [...existingIds, myId],
  })
}
```

Field names follow `get_merge_request`. Policy and glab parity: [inline-comments.md](inline-comments.md) (**Reviewer assignment**).

**Review state (request changes / approve):** No MCP tool sets reviewer review state. After inline POST, use **`mr-review-submit`**.

## Filter large diffs

```typescript
get_merge_request_diffs({
  merge_request_iid: "123",
  excluded_file_patterns: [
    "^vendor/",
    "^node_modules/",
    "package-lock\\.json",
    "\\.min\\.js$",
  ],
})
```

## Check MR with pipeline status

`get_merge_request` → `mr.pipeline.status`, `mr.detailed_merge_status`, `mr.has_conflicts`.

## Parameter alternatives

Many functions accept **`merge_request_iid` OR `source_branch`**: `get_merge_request`, `update_merge_request`, `get_merge_request_diffs`, `list_merge_request_diffs`.

## Common mistakes

- **`list_project_members`:** requires explicit `project_id` (unlike most tools that use MCP default project).
- **`create_branch`:** optional `project_id`; set it for multi-project worktrees.
- **Assignees/reviewers:** IDs only (`whoami` / `list_project_members`), never usernames.
- **`position`:** all three SHAs from `mr.diff_refs` / CLI `mr-inline-anchors` (`base_sha`, `head_sha`, `start_sha`).
- **`new_line`:** must be a `+` line from CLI `mr-inline-anchors` `result.files[path]` — [inline-comments.md](inline-comments.md).
