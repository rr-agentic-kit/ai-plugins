# Action: redesign (internal)

Change what the artifact **does**: outcome, audience, capabilities, or contracts. Structural edits allowed; document tradeoffs.

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `redesign-1-clarify` |
| `questioning.md` | `redesign-1-clarify` |
| `advisory.md` | `redesign-1-clarify` |
| `redesign-intake.md` | `redesign-1-clarify` |
| `design/design-core.md` | `redesign-2-plan` |
| `frontmatter-schemas.md` | `redesign-2-plan`, `redesign-3-apply` |
| `design/skill.md` | `redesign-3-apply` (skills) |
| `design/command.md` | `redesign-3-apply` (commands) |
| `design/agent.md` | `redesign-3-apply` (agents) |
| `readme-spec.md` | `redesign-3-apply` (skill folders) |
| `lexicon-spec.md` | `redesign-3-apply` (ACRONYMS + GLOSSARY) |
| `templates/acronyms.template.md` | `redesign-3-apply` (ACRONYMS.md) |
| `templates/glossary.template.md` | `redesign-3-apply` (GLOSSARY.md) |
| `helper-cli.md` | `redesign-3-apply` (when `scripts/`; SCRIPTABLE report waste → lean-emit recipe) |
| `template-required-map.md` | `redesign-3-apply` |
| `templates/<type>.template.md` (per `classify.md`) | `redesign-3-apply` |
| `chat-orchestration.md` | `redesign-2-plan` (workflows) |
| Prior diff report | `redesign-1-clarify` if supplied |
| Prior learn handover (`LEARN-HANDOVER.md` or chat) | `redesign-1-clarify` if supplied |
| `shared-write-gates.md` | `redesign-4-gates` |
| `gate-prompts.md`, `ui-brand.md`, `close-contract.md` | `redesign-5-close` |

## Steps

### Step 1: `redesign-1-clarify`

- **Outcome:** Delta brief and constraints are explicit.
- **Done when:** `redesign-intake.md` done-when satisfied or assumptions stated; breaking-change stance recorded; no silent scope creep beyond delta brief.

### Step 2: `redesign-2-plan`

- **Outcome:** Impact plan lists section/contract changes and tradeoffs.
- **Done when:** Each delta maps to concrete edits (add/remove/revise sections, frontmatter, stop rules); optional diff notes referenced; old audit FAILs not treated as mandatory fix list.

### Step 3: `redesign-3-apply`

- **Outcome:** Redesigned draft applied.
- **Done when:** All planned edits applied in memory or working copy; harvest new/changed jargon into `ACRONYMS.md` + `GLOSSARY.md` per `lexicon-spec.md` (ensure both exist at resolved path); if Procedure/Orchestration/close gains or keeps AskQuestion/enumerable gates, wire **Delivery channels** (or one-line N/A if Minimal clarify and no forks)—same contract as create draft. When absorbing **SCRIPTABLE** report/scaffold waste, apply `helper-cli.md` **Lean emit + schema + render**.

### Step 4: `redesign-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order (static → reflect → pre-ship → write).

### Step 5: `redesign-5-close`

- **Outcome:** User routed; re-audit recommended when write succeeded.
- **Done when:** **post-redesign-routing** or **Next Up** per `close-contract.md`; if file written, note verb-only follow-up: re-audit same path.

## Nested under improve

When parent `improve` injects path + delta brief from Ranked Absorb `redesign` opportunity detail (merge plan):

1. Treat `redesign-1-clarify` / `redesign-intake.md` done-when as satisfied — skip **all** redesign-intake AskQuestions (not only Missing delta); record breaking-change assumption once from opportunity Impact/Summary (default: partial / document in plan). Skip redesign banner and `redesign-5-close`.
2. **Load only:** this file’s Steps 2–3 (`redesign-2-plan`, `redesign-3-apply`); type design/frontmatter/readme/lexicon/chat-orchestration refs only if a planned edit touches that surface.
3. **Do not** TodoWrite `redesign-*` step ids — parent owns `improve-1…6` only.
4. **Gates:** Merge with any fix draft; parent runs `shared-write-gates.md` once on the combined set — do not run `redesign-4-gates` yourself.

Standalone redesign uses the full Ref index and Steps 1–5 above.

## Stop

Quality bar unchanged—static + reflection + pre-ship required before write. Do not claim parity with old audit PASS/FAIL lists.
