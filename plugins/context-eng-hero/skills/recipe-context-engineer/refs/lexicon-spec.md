# Lexicon companions (ACRONYMS + GLOSSARY)

Two always-required companions for a plugin (or standalone skill). Do **not** merge into one file.

| File | Holds | Example |
|------|-------|---------|
| `ACRONYMS.md` | Short forms → expansion | `PRD` → Product Requirements Document |
| `GLOSSARY.md` | Ordinary or overloaded words with a **canonical sense in this plugin** | `freeze`, `slice`, `extract`, `gate` |

If a token is both an acronym and overloaded: put expansion in **ACRONYMS**; put sense/disambiguation in **GLOSSARY** only when the expansion alone does not remove ambiguity.

Neither file is a Procedure dump or a second README.

## Placement

| Context | Path for both files |
|---------|---------------------|
| Plugin with `.cursor-plugin/` or `.claude-plugin/` | Plugin root (`ACRONYMS.md`, `GLOSSARY.md`) |
| Standalone skill (no plugin manifest parent) | Sibling next to `SKILL.md` |

## Always required

Both files must exist even with **zero** entries: H1 + empty table, or one row with `None yet`.

Templates: `templates/acronyms.template.md`, `templates/glossary.template.md`.

## Harvest (create / design / redesign / extract)

On those write paths, scan draft + co-loaded refs for:

| Source signal | Merge into |
|---------------|------------|
| Domain acronyms / initialisms | `ACRONYMS.md` |
| Overloaded / double-interpretation terms | `GLOSSARY.md` |

**Merge rules:** add missing rows; fix wrong expansions or senses; do **not** delete rows unless unused **and** the user confirms.

### Acronyms scope

Domain jargon only. Skip ubiquitous tokens (`HTTP`, `JSON`, `URL`, `OK`) unless this plugin redefines them.

### Glossary scope

Terms that would mislead an agent or human if read with a common alternate sense: product verbs, cascade nouns, action names used as nouns, domain metaphors.

## Audit / fix

| Signal | Severity / response |
|--------|---------------------|
| Missing either file | Static **FAIL** (`static.acronyms.present` / `static.glossary.present`) |
| Wrong shape (no H1 or required table columns) | Static **FAIL** (`static.*.shape`) |
| Used-but-undefined or wrong sense | Judgment **FAIL** (`skill.acronyms.coverage` / `skill.glossary.coverage`) |
| **fix** | Create or update the failing companion file(s); apply `acronyms.*` / `glossary.*` FAILs only |

Static checks presence + minimal shape only—not brittle token regex for coverage.
