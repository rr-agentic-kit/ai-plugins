# Action: fix (internal)

Apply **minimal** edits so the artifact matches **existing** intent. Prefer audit- or test-led FAIL lists.

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `fix-1-read` |
| `questioning.md` | `fix-1-read` |
| `fix-intake.md` | `fix-1-read`, `fix-2-plan` |
| `advisory.md` | `fix-2-plan` (scope check only) |
| `ui-brand.md` | `fix-1-read` (banner) |
| `frontmatter-schemas.md` | `fix-3-apply` |
| `instruction-design.md` | `fix-2-plan` |
| `skill-invocation.md` | `fix-3-apply` (skills) |
| `readme-spec.md` | `fix-3-apply` (skill folders) |
| `lexicon-spec.md` | `fix-2-plan`, `fix-3-apply` (`acronyms.*` / `glossary.*` FAILs) |
| `templates/acronyms.template.md` | `fix-3-apply` (missing/wrong ACRONYMS.md) |
| `templates/glossary.template.md` | `fix-3-apply` (missing/wrong GLOSSARY.md) |
| `helper-cli.md` | `fix-3-apply` (when `scripts/`) |
| `template-required-map.md` | `fix-3-apply` |
| `templates/<type>.template.md` (per `classify.md`) | `fix-3-apply` |
| Prior audit or test report | `fix-1-read` if supplied |
| Prior learn handover (`LEARN-HANDOVER.md` or chat) | `fix-1-read` if supplied |
| `shared-write-gates.md` | `fix-4-gates` |
| `gate-prompts.md`, `close-contract.md` | `fix-5-close` |

## Steps

### Step 1: `fix-1-read`

- **Outcome:** Target file and failure list are known; scope is fix-only.
- **Done when:** Path and failure source resolved via `questioning.md` (intake proceeds with assumptions); `fix-intake.md` done-when captured before `fix-2-plan`; file read; every FAIL id or symptom→edit mapping captured; outcome-preservation confirmed or **fix-vs-redesign** gate → redesign if outcome change.
- **Banner:** `CE ► FIX` per `ui-brand.md`.

### Step 2: `fix-2-plan`

- **Outcome:** Minimal diff plan addresses **every** listed FAIL or mapped symptom.
- **Done when:** Each failed check id maps to a concrete edit; `fix-intake.md` done-when satisfied; no unrelated refactors; eval-first minimum scope; `acronyms.*` / `glossary.*` / `static.acronyms.*` / `static.glossary.*` FAILs map to create/update of the failing companion file(s) per `lexicon-spec.md`.

### Step 3: `fix-3-apply`

- **Outcome:** Edits applied to draft.
- **Done when:** All planned fixes applied in memory or working copy—including lexicon companion creates/updates when those ids failed.

### Step 4: `fix-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order.

### Step 5: `fix-5-close`

- **Outcome:** User routed to next action or done.
- **Done when:** **post-fix-routing** AskQuestion per `gate-prompts.md`; on selection, skill continues; else **Next Up** per `close-contract.md`.

## Stop

No scope expansion. When audit-led, fix **every** FAIL (critical, major, minor)—no "critical only" shortcut.
