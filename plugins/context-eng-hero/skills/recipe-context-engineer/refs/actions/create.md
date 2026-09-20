# Action: create (internal)

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `create-1-classify` |
| `questioning.md` | `create-1-classify`, `create-2-clarify` |
| `classify.md` | `create-1-classify` |
| `advisory.md` | `create-2-clarify` |
| `ui-brand.md` | `create-1-classify` (banner) |
| `frontmatter-schemas.md` | `create-3-draft` |
| `design/design-core.md` | `create-3-draft` |
| `design/skill.md` | `create-2-clarify`, `create-3-draft` (skills) |
| `design/command.md` | `create-3-draft` (commands) |
| `design/agent.md` | `create-3-draft` (agents) |
| `design/inline-executor.md` | `create-3-draft` (`refs/executors/*.md` or orchestrator gaining Task spawn) |
| `templates/executor.template.md` | `create-3-draft` (inline executor) |
| `templates/task-prompt.template.md` | `create-3-draft` (orchestrator parent spawning Tasks) |
| `gate-prompts.md` | `create-2-clarify` (skills: skill-ux-delivery), `create-5-close` |
| `readme-spec.md` | `create-3-draft` (skill folders) |
| `templates/readme.template.md` | `create-3-draft` (skill README) |
| `lexicon-spec.md` | `create-3-draft` (ACRONYMS + GLOSSARY) |
| `templates/acronyms.template.md` | `create-3-draft` (ACRONYMS.md) |
| `templates/glossary.template.md` | `create-3-draft` (GLOSSARY.md) |
| `helper-cli.md` | `create-3-draft` (when `scripts/`; SCRIPTABLE report waste → lean-emit recipe) |
| `chat-orchestration.md` | `create-3-draft` (workflows) |
| `template-required-map.md` | `create-3-draft` |
| `templates/<type>.template.md` (per `classify.md`) | `create-3-draft` |
| Prior test/audit FAIL | `create-2-clarify` if supplied |
| `shared-write-gates.md` | `create-4-gates` |
| `close-contract.md` | `create-5-close` |

## Steps

### Step 1: `create-1-classify`

- **Outcome:** Artifact type is the narrowest fit.
- **Done when:** Type named via `classify.md` + `questioning.md` if unknown—no draft started until type known.
- **Banner:** `CE ► CREATE` per `ui-brand.md`.

### Step 2: `create-2-clarify`

- **Outcome:** Outcome, audience, failure mode, and (for skills) **invoke mode** + **skill UX (input/delivery)** are resolved (or explicitly deferred with open questions listed).
- **Done when:** Clarify fields answered per `questioning.md` (one question at a time); skills: invoke mode per `design/skill.md` **and** skill UX resolved via **skill-ux-delivery** (`gate-prompts.md`) or deferred as an open question; no REQUIRED hard-stop at intake.
- **Eval-first:** If user supplied test FAIL or audit FAIL, treat as **minimum write scope**.

### Step 3: `create-3-draft`

- **Outcome:** Draft file content from template; `<!-- REQUIRED -->` markers replaced per `template-required-map.md`.
- **Done when:** Full draft in memory; workflow steps include `todo_id` column if type is workflow; skill: `description` ≤160 chars and matches invoke mode; skill folder: sibling README per `readme-spec.md` drafted or defer reason recorded; `ACRONYMS.md` + `GLOSSARY.md` at resolved path per `lexicon-spec.md` (empty table OK—companions ship every skill/plugin create); skills: **Delivery channels** wired from skill-UX choice into README **UX → Clarify/Close** and SKILL **Orchestration** / Execution rules (or one-line N/A if Minimal clarify and no enumerable forks). When the draft absorbs **SCRIPTABLE** report/scaffold waste, apply `helper-cli.md` **Lean emit + schema + render** (schemas + Jinja under `refs/templates/reports/`; thin render script)—not more prose procedure.
- **Skill folder draft order:** (1) README spec from `templates/readme.template.md` if missing or user supplied spec only; (2) `SKILL.md` from README + `templates/skill.template.md`; (3) ensure `ACRONYMS.md` + `GLOSSARY.md` at plugin root (or skill sibling if standalone)—harvest jargon from draft + co-loaded refs. If README already exists and user asked for `SKILL.md`, derive from README—do not invent a second spec.
- **Delivery from UX gate:** Inject a short Question delivery / Orchestration constraint citing `questioning.md` **Delivery channels**—prefer AskQuestion when gates exist; text-mode same options mandatory; do not stall. Never rewrite Purpose/When/Procedure from the UX choice alone.
- **README → SKILL derivation map** (per `readme-spec.md` reconstructability):

  | SKILL section | README source |
  |---------------|---------------|
  | `description` | Constraints + Use when / Avoid when condensed |
  | Purpose | **Why** |
  | When to use | **When → Use when** |
  | When not to use | **When → Avoid when** (+ What out-of-scope if unique) |
  | Actions table | **Actions** (id, outcome; omit Pick when) |
  | Procedure | Constraints phases + UX habit names only |
  | Exit conditions | Constraints stops + UX clarify caps |
  | Execution rules | **UX** subsections (incl. Delivery channels / N/A) |
  | Orchestration | **UX → Clarify/Close** + skill-UX choice |

### Step 4: `create-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order.

### Step 5: `create-5-close`

- **Outcome:** User routed to next action or done.
- **Done when:** **post-create-routing** AskQuestion per `gate-prompts.md`; on selection, skill continues to routed action; else **Next Up** per `close-contract.md`.

## Stop

Do not bypass reflection or pre-ship. Do not write outside agreed plugin-relative paths.
