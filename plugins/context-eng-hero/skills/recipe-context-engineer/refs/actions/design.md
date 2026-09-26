# Action: design assist write (internal)

Conditional procedure when skill **Classify** + **Clarify** ends with writing a file this turn. Default design assist (no write) does **not** load this file.

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `design-1-classify` |
| `questioning.md` | `design-1-classify`, `design-2-clarify` |
| `classify.md` | `design-1-classify` |
| `advisory.md` | `design-2-clarify` |
| `frontmatter-schemas.md` | `design-3-draft` |
| `design/design-core.md` | `design-3-draft` |
| `design/skill.md` | `design-2-clarify`, `design-3-draft` (skills) |
| `design/command.md` | `design-3-draft` (commands) |
| `design/agent.md` | `design-3-draft` (agents) |
| `design/inline-executor.md` | `design-3-draft` (`refs/executors/*.md` or orchestrator gaining Task spawn) |
| `templates/executor.template.md` | `design-3-draft` (inline executor) |
| `templates/task-prompt.template.md` | `design-3-draft` (orchestrator parent spawning Tasks) |
| `gate-prompts.md` | `design-2-clarify` (skills: skill-ux-delivery) |
| `readme-spec.md` | `design-3-draft` (skill folders) |
| `templates/readme.template.md` | `design-3-draft` (skill README) |
| `lexicon-spec.md` | `design-3-draft` (ACRONYMS + GLOSSARY) |
| `templates/acronyms.template.md` | `design-3-draft` (ACRONYMS.md) |
| `templates/glossary.template.md` | `design-3-draft` (GLOSSARY.md) |
| `helper-cli.md` | `design-3-draft` (when `scripts/` exists **or** deterministic fetch/filter/id-keyed write) |
| `template-required-map.md` | `design-3-draft` |
| `templates/<type>.template.md` (per `classify.md`) | `design-3-draft` |
| `shared-write-gates.md` | `design-4-gates` |
| `close-contract.md`, `ui-brand.md` | After gates |

## Triggers (all required)

- User explicitly requests writing a file (path stated or approved after one ask).
- Classify/clarify sufficient to draft, or open questions listed explicitly in output.

If the user only wanted guidance, **AskQuestion**: finish here or run **create** action.

## Steps

### Step 1: `design-1-classify`

- **Outcome:** Artifact type is the narrowest fit.
- **Done when:** `classify.md` satisfied; type named (may already be done earlier this turn).

### Step 2: `design-2-clarify`

- **Outcome:** Outcome, audience, failure mode, and (for skills) **invoke mode** + **skill UX (input/delivery)** resolved or open questions listed.
- **Done when:** `questioning.md` satisfied; skills: invoke mode **and** skill UX via **skill-ux-delivery** (`gate-prompts.md`) resolved or deferred as open questions; ready to draft or gaps explicit.

### Step 3: `design-3-draft`

- **Outcome:** Template-shaped draft at approved plugin-relative path.
- **Done when:** Full draft in memory/working copy; markers replaced per `template-required-map.md`; eval-first minimum when FAIL list supplied; skills: empty `ACRONYMS.md` + `GLOSSARY.md` companions ship if missing; **Delivery channels** from skill-UX choice wired into README **UX** + SKILL Orchestration / Execution rules (or one-line N/A if no enumerable forks).
- **Skill folder draft order:** Same as **create**—README spec first if missing; `SKILL.md` from README when both ship; ensure `ACRONYMS.md` + `GLOSSARY.md` at resolved path per `lexicon-spec.md`. If write target is only README, use **extract** ingestion rules on existing `SKILL.md`.
- **Delivery from UX gate:** Same as **create**—inject Delivery channels constraint from skill-UX choice; do not rewrite Purpose/When/Procedure from that gate alone.
- **README ↔ SKILL derivation:** Same reconstructability map as **create** (`readme-spec.md` table). README-only write: follow **extract** section map. SKILL-only write from existing README: derive per create map—do not invent parallel spec.

### Step 4: `design-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order.

## Stop

Do not skip gates because "it's only design assist." No silent invention of missing business facts—list open questions if clarify incomplete.
