# Command audit rubric

Map judgment FAILs to labels in `failure-patterns.md` for narrative. Evaluate **Judgment** only in audit step 3. **Static** ids are produced by `scripts/audit_static.py`.

## Static (script)

| id | Severity |
|----|----------|
| `static.frontmatter.delimiters` | critical |
| `static.frontmatter.parseable` | critical |
| `static.keys.required` | critical |
| `static.name.format` | critical |
| `static.name.path-match` | critical |
| `static.description.present` | critical |
| `static.paths.no-parent-segment` | critical |
| `static.paths.no-absolute` | major |
| `static.sections.required` | critical |
| `static.links.internal-resolve` | major |
| `static.links.https-only` | critical |

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

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `command.description.user-facing` | minor | `description` is user-facing purpose without internal layout jargon |
| `command.noise.signal-ratio` | minor | No filler paragraphs without behavioral constraints |
