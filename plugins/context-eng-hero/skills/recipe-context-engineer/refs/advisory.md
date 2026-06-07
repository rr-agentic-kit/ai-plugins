# Advisory (design partner)

Loaded in the **Advise** orchestration step and after **Gather** in Clarify. Run for **create**, **design**, **extract**, **fix**, and **redesign**—skip for **audit**, **test**, and **diff** (diagnosis-only).

## Hidden-requirements catalog

Check before authoring. Surface gaps the user did not mention; do not re-ask what they already answered.

### Skill

- **Single outcome** — Purpose must not bundle two unrelated outcomes; suggest split if detected
- **Anti-triggers** — "When not to use" declared; no silent overlap with sibling skills
- **Stop points** — Each orchestration step has a done-when; no infinite loops
- **Progressive disclosure** — Body ≤ ~200 lines or refs plan declared; heavy detail in `refs/`
- **Audience boundary** — Human vs agent vs both explicit; not "everyone"

### Command

- **Output format pinned** — Fixed sections or template; not free-form prose
- **Pipe-ability** — Stdout-friendly when output may feed other tools
- **Error exit codes** — Failure modes map to predictable behavior
- **argument-hint** — Declared in frontmatter when args are expected
- **No internal ref paths** — Body delegates to skill action; no `refs/` or `plugins/` paths in user-facing body

### Agent

- **Tool boundary** — Allowlist or denylist explicit; not "use tools as needed"
- **Stop conditions** — Per outcome; agent knows when to stop without user nudge
- **Isolation mode** — Subagent vs inline chosen and justified
- **Max turns bounded** — No unbounded "continue until done"

### Rule

- **Glob specificity** — Over-broad globs = false-positive risk; surface tradeoff
- **alwaysApply vs scoped** — Tradeoff surfaced when `alwaysApply: true` affects whole repo
- **Conflict with siblings** — Overlapping rules on same paths flagged

### Workflow

- **todo_id per step** — Every step has a trackable id for TodoWrite
- **Delegation table complete** — Each step maps to artifact type or explicit "inline"
- **Loop bounds** — Retry/repeat steps declare max rounds and exit
- **No implicit continue** — No step that means "keep going until done" without a bound

## Tradeoff presentation protocol

- Format: `Option A: [desc]. Pro: X. Con: Y.`
- Never present more than 3 options per decision
- Always include a **simplest viable** option
- **AskQuestion** for enumerable choices (2–3); open text for genuinely open-ended
- Cap: at most **3 advisory items** per turn; critical and major gaps first

## Design critique triggers

Call out before writing (do not silently author past these):

| Trigger | Response |
|---------|----------|
| Two unrelated outcomes in Purpose | Suggest split into two artifacts |
| Audience = "everyone" or unspecified | Require narrowing before proceeding |
| No failure mode for agent/workflow | Flag as **critical** gap |
| Body > 200 lines without refs plan | Flag as **NOISE** risk; propose ref extraction |

## When to skip

- User message already addresses every item in the catalog for the detected type → skip Advise silently (0 gaps)
- Action is audit, test, or diff → Advise not loaded
