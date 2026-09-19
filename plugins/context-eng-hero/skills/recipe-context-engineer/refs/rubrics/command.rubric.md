# Command audit rubric

Map judgment FAILs to labels in `failure-patterns.md` for narrative. Evaluate **Judgment** only in audit step 3. **Static** ids are produced by `scripts/audit_static.py`—do not re-score manually unless script skipped.

## Judgment

### Critical

| id | Severity | PASS when |
|----|----------|-----------|
| `command.delegation.action-id` | critical | Body contains `Execute **Action:` and a skill id; no `refs/` or `plugins/` filesystem paths in the command body |
| `command.input.required` | critical | **REQUIRED** inputs listed; behavior when missing stated (ask once, stop, etc.) |
| `command.routing.no-chain-only` | critical | Body does not route solely by “invoke `/other-command`” steps without a skill **Action** owning work |

### Major

| id | Severity | PASS when |
|----|----------|-----------|
| `command.output.shape` | major | **Output** section names report fields or write/stop outcomes (quote heading content) |
| `command.side-effects` | major | States whether file edits are allowed or forbidden for this command |
| `command.progress.todowrite` | major | **Progress** section requires TodoWrite with step ids matching `refs/actions/<verb>.md` |
| `command.consistency` | major | Delegated **Action** verb matches the command’s stated purpose |
| `command.clarify.delivery-channels` | major | If body mentions AskQuestion or enumerable clarify/close gates: states text-mode fallback (same options as prose; no stall). Else one-line N/A or PASS if AskQuestion absent |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `command.description.user-facing` | minor | `description` is user-facing purpose without internal layout jargon; ≤160 recommended |
| `command.description.recommended-length` | minor | `description` ≤160 characters one sentence, or user explicitly accepted over-budget |
| `command.argument-hint.when-args` | minor | `argument-hint` present when Input contract expects args; omit when no args |
| `command.noise.signal-ratio` | minor | No filler paragraphs without behavioral constraints |
| `command.refs.load-efficiency` | minor | Files in this artifact's **Load** list do not duplicate each other's content; no ref is a strict subset of another co-loaded ref |
