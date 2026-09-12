# Action: extract (internal)

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `extract-1-ingest` |
| `questioning.md` | `extract-1-ingest`, `extract-2-classify` |
| `advisory.md` | `extract-2-classify` |
| `classify.md` | `extract-2-classify` |
| `frontmatter-schemas.md` | `extract-3-draft` |
| `instruction-design.md` | `extract-3-draft` |
| `skill-invocation.md` | `extract-3-draft` (skills) |
| `readme-spec.md` | `extract-3-draft` (skill folders) |
| `templates/readme.template.md` | `extract-3-draft` (skill README output) |
| `lexicon-spec.md` | `extract-3-draft` (ACRONYMS + GLOSSARY harvest) |
| `templates/acronyms.template.md` | `extract-3-draft` (ACRONYMS.md) |
| `templates/glossary.template.md` | `extract-3-draft` (GLOSSARY.md) |
| `helper-cli.md` | `extract-3-draft` (when `scripts/`) |
| `template-required-map.md` | `extract-3-draft` |
| `templates/<type>.template.md` (per `classify.md`) | `extract-3-draft` |
| `shared-write-gates.md` | `extract-4-gates` (file write only) |
| `gate-prompts.md`, `ui-brand.md`, `close-contract.md` | `extract-5-close` |
| Prior test/audit FAIL | `extract-1-ingest` if supplied |

## Steps

### Step 1: `extract-1-ingest`

- **Outcome:** Source material understood; noise stripped.
- **Done when:** User chat/workflow/notes ingested; conversational filler removed; any probe FAIL or miss noted as write target.

### Step 2: `extract-2-classify`

- **Outcome:** Target type and provenance recorded.
- **Done when:** Type chosen per `classify.md`; provenance block lists **source**, **assumptions**, **open questions** (no secrets in source); skills: invoke mode stated or deferred.

### Step 3: `extract-3-draft`

- **Outcome:** Template-shaped **minimum** draft produced (eval-first).
- **Done when:** All template sections filled or gaps explicitly marked; only constraints justified by source or observed FAIL—no anticipated thickening; workflow includes `todo_id` if applicable.
- **Skill README** (output `skills/<name>/README.md`): Read `SKILL.md` + progressive-disclosure refs for **constraints** (invoke mode, gates, eval-first, paths)—**not** to dump **Procedure** or Load chains. Fill `templates/readme.template.md` per `readme-spec.md` scannable section model and clarity rules. Provenance lists source paths (`SKILL.md`, ref paths used) + assumptions + open questions.
- **Lexicon harvest** (when writing skill/plugin artifacts): Scan draft + co-loaded refs; merge domain acronyms into `ACRONYMS.md` and overloaded terms into `GLOSSARY.md` at resolved path per `lexicon-spec.md`. Create empty companions if missing.
- **README section map (extract):**

  | README section | Source in SKILL / refs |
  |----------------|------------------------|
  | **Why** | Purpose; audience from advisory |
  | **What** (+ `### Verification`) | Domain, types, boundaries; static + rubric + probe concepts |
  | **Actions** | SKILL **Actions** table (id, outcome); **Pick when** from `classify.md` routing (includes **learn** when present) |
  | **When → Use when** | SKILL **When to use** |
  | **When → Avoid when** | SKILL **When not to use** (dedupe What out-of-scope) |
  | **Philosophy** | Eval-first, scoped-only, gates from advisory + Constraints facts |
  | **UX** (`###` subsections) | Execution rules, Exit conditions, `questioning.md`, `close-contract.md`, `ui-brand.md` |
  | **Design notes** | Frontmatter tradeoffs (`disable-model-invocation`, dual close, STATIC SKIPPED) when ≥2 |
  | **Constraints** | Invoke flags, write gates, eval-first, path rules |
  | **Notes** | Script paths, rubric/prompt dirs—footer only |

### Step 4: `extract-4-gates`

- **Outcome:** Shared write gates evaluated when user requested a file.
- **Done when:** If write requested: all four gates in `refs/actions/shared-write-gates.md` completed (same contract as **create**). If chat-only: N/A with reason.

### Step 5: `extract-5-close`

- **Outcome:** Deliverable returned; loop closed.
- **Done when:** Draft + provenance in chat, or file written only if gates PASSED; **post-create-routing** or **Next Up** per `close-contract.md`.

## Stop

No silent invention of missing business facts—list open questions explicitly.
