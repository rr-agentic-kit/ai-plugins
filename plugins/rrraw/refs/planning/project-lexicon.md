# project-lexicon

**Owner:** Host-repo domain lexicon under `docs/` — skill-owned (Discover + Plan). Silent create/merge only. Not validator input. Not a cascade stem. Not Discover parking (`docs/rr/`).

**Load when:** After [compose-prose.md](../../skills/rr-discovery/refs/compose-prose.md) succeeds (every cascade `.md` persist); after `--from-code` research persist ([from-code.md](../../skills/rr-discovery/refs/from-code.md)).

**Does not:** AskQuestion about terms; mint empty files at `--setup`; overwrite or delete rows; dump rrraw plugin vocabulary into host files; let compose Task agents write these files.

## Paths

| File | Path |
|------|------|
| Glossary | `{PROJECT_ROOT}/docs/GLOSSARY.md` |
| Acronyms | `{PROJECT_ROOT}/docs/ACRONYMS.md` |

Project-wide SoT for any agent — not under `docs/rr/{track}/`.

## Shape

Mirror context-eng-hero templates (H1 + table). Prefer create-with-first-row over empty “None yet” mint at setup.

**Acronyms**

```markdown
# Acronyms

| Acronym | Expansion | Notes |
|---------|-----------|-------|
| WMS | Warehouse Management System | Host domain |
```

**Glossary**

```markdown
# Glossary

| Term | Meaning | Notes |
|------|---------|-------|
| lane | Scheduled capacity corridor between hubs | Host domain |
```

Empty table only transient until first row. Optional `Notes` column may be omitted on a row but keep header stable once created.

## Silence law

- Never AskQuestion / surface lexicon in pre-save or Q&A.
- Never invent rows at `--setup` or resolve/`--sync-agent-config` (resolve may only repair H1/table headers when files already exist — never invent rows).
- Compose Task agents must not write these files ([contracts.md](contracts.md) / compose adapter).

## Merge rules (additive only)

| Rule | Behavior |
|------|----------|
| Insert | Add missing keys only (case-insensitive match on Acronym / Term) |
| Preserve | Never overwrite existing Meaning / Expansion / Notes |
| Delete | Never remove rows |
| Create | If file missing → create on first successful merge only (with ≥1 new row) |
| Repair | If file exists with wrong shape → fix H1 / table headers silently; preserve all rows |

**Which tokens qualify (judgment):** host **domain** terms from cascade/session evidence — acronyms and overloaded domain words the project uses with a specific sense.

**Exclude**

| Class | Examples |
|-------|----------|
| rrraw / plugin vocabulary | `freeze`, `slice`, `spine`, `cascade`, `challenge`, `nature`, Discover/Plan ceremony terms |
| Ubiquitous web/tech unless the *project* redefines them | HTTP, JSON, URL, API (as generic), REST |
| Plugin-root companions | Do **not** copy `plugins/rrraw/GLOSSARY.md` / `ACRONYMS.md` into host `docs/` |
| Humanize AI-tell wipe | Not `skills/docs/rr-humanize` `lexicon.md` — different concern |

## Triggers

| Trigger | Behavior |
|---------|----------|
| After compose-prose succeeds (every cascade `.md` persist) | Scan humanized prose + co-persisted item labels for new acronyms / overloaded domain terms → merge |
| After `--from-code` research persist | Seed from `session_state.from_code_evidence.domain_language` (and related domain strings) before/with first compose — same merge rules |
| Files missing | Create on first successful merge only |
| Files exist, wrong shape | Repair H1/table headers silently; preserve rows |

## Ownership / tiers

| Concern | |
|---------|--|
| Writers | Discover + Plan skills only (via compose-prose / from-code hooks) |
| Consumers | When present, agents read both files for project terms ([agent.plan.md](agent.plan.md)) |
| Validator | **Not** input |
| Cascade / version | **Not** a stem; no `doc_rev` / pins |
| vs `docs/rr/` parking | Distinct from `tech.md` / `later.md` / `future.md` mechanism parking |

## Anti-echo

Single SoT for write semantics is **this file**. Skills point here; do not restate merge tables in SKILL bodies. Plugin-root `GLOSSARY.md` / `ACRONYMS.md` stay marketplace audit companions — never merge those into host `docs/`.
