# Advisory (design partner)

Loaded in the **Advise** orchestration step and after **Gather** in Clarify. Run for **create**, **design**, **extract**, **fix**, and **redesign**—skip for **audit**, **test**, and **diff** (diagnosis-only).

## Eval-first authoring

Default create/fix path (Anthropic eval-first): **observe a miss, write the minimum that would pass, then gates**—do not front-load research or anticipated constraints.

| Signal | Authoring default |
|--------|-------------------|
| Failed **test** probe, audit FAIL, or user-reported miss | Write/fix only what that FAIL requires; re-probe before thickening |
| **Extract** notes or chat transcript | Template-shaped draft + provenance; gaps = open questions—not invented policy |
| No observed FAIL yet | Smallest draft that satisfies clarify (outcome, audience, failure mode); thicken after first FAIL |
| “Research how others do it” / web browse | **Optional** local sibling pattern match only—not a mandatory phase before draft |

**Thicken from FAILs, not anticipation:** add refs, steps, or rules only when a probe, audit, or live miss proves the gap. Research-as-phase produces bloated READMEs and echo.

## Goldilocks (over/under-spec)

Challenge before writing (see `instruction-design.md` **Degrees of freedom**):

| Signal | Advisory response |
|--------|-------------------|
| Long if-else trees for rare edges | **Over-spec** — collapse to one example + stop rule or low-freedom script |
| “Use best judgment” on irreversible action | **Under-spec** — add exact steps or `scripts/` entry |
| Duplicate policy in SKILL + ref + README | **Echo** — link once; pick canonical layer |
| Body >200 lines without refs plan | **NOISE** — extract refs (one-level deep) |

## README role (bidirectional spec)

Skills that ship to humans need a sibling **README** per `readme-spec.md`—create must not ship definition-only. README holds **Why**, **What**, **When**; `SKILL.md` holds **Procedure**. Use `templates/readme.template.md` for shape.

| Direction | Default action |
|-----------|----------------|
| README from existing `SKILL.md` | **extract** |
| `SKILL.md` from existing README | **create** / **design** (README spec first if missing) |

Do **not** clone legacy Goals/Scope/Audience/When-to-use section scripts. Do **not** paste Procedure into README.

## Hidden-requirements catalog

Check before authoring. Surface gaps the user did not mention; do not re-ask what they already answered.

### Skill / Skill+Ref

- **Single outcome** — Purpose must not bundle two unrelated outcomes; suggest split if detected
- **Anti-triggers** — "When not to use" declared; no silent overlap with sibling skills
- **Stop points** — Each orchestration step has a done-when; no infinite loops
- **Progressive disclosure** — Body ≤ ~200 lines or refs plan declared; heavy detail in `refs/`; **one hop** from SKILL (no ref→ref chains)
- **Audience boundary** — Human vs agent vs both explicit; not "everyone"
- **Invoke mode** — Auto / Slash-or-parent / Background chosen before drafting `description` and flags (`refs/skill-invocation.md`)
- **Scripts folder** — If `scripts/` exists: agent **runs** helpers via shell; do not paste script bodies into SKILL (`refs/helper-cli.md`)
- **README** — Sibling spec with Why/What/When; does not restate Procedure (`refs/readme-spec.md`)

**Skill+Ref additional:**

- **Ref protocol** — Progressive disclosure names which ref for which subtask; fallback when no ref matches
- **Layer separation** — Invariant procedure in SKILL; variant/detail in refs only (`rubrics/skill-ref.rubric.md`)
- **Ref standalone** — Each ref readable alone with **Purpose** + **Load** back to parent

### Ref file

- **Standalone purpose** — One falsifiable sentence without opening parent SKILL
- **No base duplication** — Does not restate parent Procedure or Purpose
- **Load path** — States parent skill and which step Read this file
- **No ref chain** — Does not link to other refs for required context

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
| `user-invocable: false` as sole control on internal skill | Flag **wrong lever** — auto-trigger may still run; see `skill-invocation.md` |
| Skill `description` >160 chars without justification | Flag **discovery bloat** — rewrite to one sentence ≤160 before gates |
| Self-invoke skill with audit/fix/redesign verbs in `description` | Flag **invoke-fit** — outcome-first; no ambient trigger stuffing |

## When to skip

- User message already addresses every item in the catalog for the detected type → skip Advise silently (0 gaps)
- Action is audit, test, or diff → Advise not loaded
