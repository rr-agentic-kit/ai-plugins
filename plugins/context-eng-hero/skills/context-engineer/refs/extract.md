# Extract procedure (reference)

Used by **Action: extract** via `refs/actions/extract.md`. Summary for authors:

## Goal

Turn **chat transcript, ad-hoc instructions, or working notes** into a **single durable artifact** (skill, command, agent, rule, or workflow) with **provenance**.

## Provenance block (required in output)

Record in the artifact or in the chat summary:

- **Source**: which chat/thread or pasted excerpt (no secrets).
- **Assumptions**: what you inferred because the source was silent.
- **Open questions**: what still needs a human decision before **rewrite** to production paths.

## Steps (high level)

1. Classify artifact type (narrowest fit).
2. Pull stable constraints and policies from the source; drop conversational filler.
3. Map to the matching `*.template.md` sections; mark `<!-- REQUIRED -->` gaps.
4. If type is ambiguous, stop after a typed **draft** plus questions—do not pretend completeness.

Cross-link: `instruction-design.md`, `frontmatter-schemas.md`, `pre-ship-checklist.md` before any write.
