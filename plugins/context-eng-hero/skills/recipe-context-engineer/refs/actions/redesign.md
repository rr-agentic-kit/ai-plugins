# Action: redesign (internal)

Change what the artifact **does**: outcome, audience, capabilities, or contracts. Structural edits allowed; document tradeoffs.

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `redesign-1-clarify` |
| `questioning.md` | `redesign-1-clarify` |
| `advisory.md` | `redesign-1-clarify` |
| `redesign-intake.md` | `redesign-1-clarify` |
| `instruction-design.md` | `redesign-2-plan` |
| `frontmatter-schemas.md` | `redesign-2-plan`, `redesign-3-apply` |
| `skill-invocation.md` | `redesign-3-apply` (skills) |
| `readme-spec.md` | `redesign-3-apply` (skill folders) |
| `helper-cli.md` | `redesign-3-apply` (when `scripts/`) |
| `template-required-map.md` | `redesign-3-apply` |
| `templates/<type>.template.md` (per `classify.md`) | `redesign-3-apply` |
| `chat-orchestration.md` | `redesign-2-plan` (workflows) |
| Prior diff report | `redesign-1-clarify` if supplied |
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
- **Done when:** All planned edits applied in memory or working copy.

### Step 4: `redesign-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order (static → reflect → pre-ship → write).

### Step 5: `redesign-5-close`

- **Outcome:** User routed; re-audit recommended when write succeeded.
- **Done when:** **post-fix-routing** or **Next Up** per `close-contract.md`; if file written, note verb-only follow-up: re-audit same path.

## Stop

Quality bar unchanged—static + reflection + pre-ship required before write. Do not claim parity with old audit PASS/FAIL lists.
