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
| `instruction-design.md` | `design-3-draft` |
| `skill-invocation.md` | `design-3-draft` (skills) |
| `readme-spec.md` | `design-3-draft` (skill folders) |
| `templates/readme.template.md` | `design-3-draft` (skill README) |
| `helper-cli.md` | `design-3-draft` (when `scripts/`) |
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

- **Outcome:** Outcome, audience, and failure mode resolved or open questions listed.
- **Done when:** `questioning.md` satisfied; ready to draft or gaps explicit.

### Step 3: `design-3-draft`

- **Outcome:** Template-shaped draft at approved plugin-relative path.
- **Done when:** Full draft in memory/working copy; markers replaced per `template-required-map.md`; eval-first minimum when FAIL list supplied.
- **Skill folder draft order:** Same as **create**—README spec first if missing; `SKILL.md` from README when both ship. If write target is only README, use **extract** ingestion rules on existing `SKILL.md`.
- **README ↔ SKILL derivation:** Same reconstructability map as **create** (`readme-spec.md` table). README-only write: follow **extract** section map. SKILL-only write from existing README: derive per create map—do not invent parallel spec.

### Step 4: `design-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order.

## Stop

Do not skip gates because "it's only design assist." No silent invention of missing business facts—list open questions if clarify incomplete.
