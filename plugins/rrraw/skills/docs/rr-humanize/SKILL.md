---
name: _oa-humanize-skill
description: >-
  Humanize docs and MR prose. Load for generate/rewrite, AI-tell removal, or
  --voice/--tone flags. Keywords: humanize, de-AI, readability.
---

# Humanize

Route **generate** (draft from brief) and **rewrite** (reshape existing text) through progressive refs and the helper CLI.

## Progressive load

| Trigger | Load |
|---------|------|
| No source text | `refs/generate.md`, `refs/readability.md` |
| Source text present | `refs/rewrite.md`, `refs/readability.md` |
| User flags (`--voice`, `--tone`) | `refs/params.md` first |
| After one `scan` | `refs/lexicon.md` only if result has judgment categories |
| Register unclear | `suggest-register` CLI; if low confidence → `refs/register.md` |
| Structure-only ask | `refs/readability.md` |
| Words-only ask | `scan` then `refs/lexicon.md` on judgment hits |

**CLI:** one call per step — `scripts/README.md`. Budget: rewrite ≤2 calls; generate ≤1 after draft.

## Workflows

**Generate:** lock facts → `active` + `plain` unless flags → draft under readability → optional `scan` → claim check → deliver.

**Rewrite:** parse flags → `scan` → meaning lock → optional `apply-safe` → LLM reshape (judgment hits + readability) → claim check → output.

Empty rewrite input → ask for text. Empty generate brief → ask what to write.

## Refs

| File | Role |
|------|------|
| [generate.md](refs/generate.md) | Draft workflow |
| [rewrite.md](refs/rewrite.md) | Reshape workflow |
| [readability.md](refs/readability.md) | Structure and psych rules |
| [lexicon.md](refs/lexicon.md) | Judgment-only replacements |
| [register.md](refs/register.md) | Voice and tone |
| [params.md](refs/params.md) | Flag enums and errors |

Paths relative to plugin root: `skills/docs/rr-humanize/...`
