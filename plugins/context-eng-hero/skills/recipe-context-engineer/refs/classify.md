# Classify (artifact types)

Pick the **narrowest** type. Load at orchestration step 2 and action classify steps.

## Types

| Type | When |
|------|------|
| **Skill** | Reusable procedure or policy; single SKILL.md, no sibling `refs/` pack |
| **Skill+Ref** | Base SKILL.md + `refs/` (or `references/`) loaded per progressive disclosure—variant or deep-dive refs |
| **Ref file** | Skill-private `refs/*.md` (or `references/*.md`) — not an entry point; loaded because parent SKILL / action Ref index names it |
| **Command** | Named slash entry with fixed input/output contract |
| **Agent** | Role with tools, boundaries, and stop conditions |
| **Rule** | Always-on or glob-scoped constraint |
| **Workflow** | Multi-step orchestration with delegation and per-step outputs |

Do not merge types. A folder with SKILL.md + `refs/` is **Skill+Ref**, not plain **Skill**.

## Detection hints

| Signal | Type |
|--------|------|
| `skills/<name>/SKILL.md` only | Skill |
| `skills/<name>/SKILL.md` + `refs/` or `references/` | Skill+Ref |
| `skills/<name>/refs/<topic>.md` (no SKILL edit) | Ref file |
| `commands/<name>.md` | Command |
| `agents/<name>.md` | Agent |
| `.cursor/rules/*.mdc` or `rules/` | Rule |
| `*workflow*.md` with Steps + Delegation | Workflow |

Templates: `templates/skill.template.md` (Skill or Skill+Ref), `templates/ref-file.template.md`, plus type-specific templates in `templates/`.

## Routing (fix vs redesign)

**Eval-first:** Prefer **test** or **audit** FAIL lists as minimum fix scope before adding anticipated rules.

| Signal | Action |
|--------|--------|
| Audit verdict FAIL | **fix** + audit report |
| Test probe FAIL, same contract | **fix** + test report |
| Live run miss (patch or friction) on existing skill | **learn** → then **fix** or **redesign** from handover |
| Learn handover (approved topics preserve outcome) | **fix** + `LEARN-HANDOVER.md` |
| Learn handover (any topic changes outcome/audience/capabilities) | **redesign** + `LEARN-HANDOVER.md` |
| Test FAIL / user story = wrong capability or outcome | **redesign** |
| User: add step, remove gate, change audience | **redesign** |
| User: wording, typo, violates own stop rule | **fix** |
| Extract → production with resolved open questions | **redesign** (first ship) or **fix** (polish only) |

When ambiguous → **fix-vs-redesign** gate (`gate-prompts.md`).

## README routing (skill folders)

Bidirectional contract per `readme-spec.md`. Pick action from **write target**, not from "update the skill pack" alone.

| Write target | Existing sibling | Action |
|--------------|------------------|--------|
| `skills/<name>/README.md` | `SKILL.md` (+ refs) | **extract** (definition → spec) |
| `skills/<name>/SKILL.md` | README as spec (or user supplies draft spec) | **create** / **design** (spec → definition) |
| Both README and `SKILL.md` in one turn | — | One **AskQuestion**: which file is the write target this turn? |
| New skill folder (no files yet) | — | **create** — draft README spec first, then `SKILL.md` per `readme-spec.md` draft order |

**Extract** output path is `skills/<name>/README.md` when user asks to "write the README", "human spec", or "extract README from skill."

**Create/design** when README exists: derive `SKILL.md` from README—do not invent a parallel spec.

Detection: `skills/<name>/README.md` → artifact type **skill-readme** for static audit (`detect.py`).
