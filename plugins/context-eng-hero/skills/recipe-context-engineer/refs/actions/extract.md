# Action: extract (internal)

## Load (Read)

- `disambiguation.md`
- `advisory.md`
- `instruction-design.md`
- `frontmatter-schemas.md`
- Matching artifact template (same set as create)

## Steps

### Step 1: `extract-1-ingest`

- **Outcome:** Source material understood; noise stripped.
- **Done when:** User chat/workflow/notes ingested; conversational filler removed.

### Step 2: `extract-2-classify`

- **Outcome:** Target type and provenance recorded.
- **Done when:** Type chosen; provenance block lists **source**, **assumptions**, **open questions** (no secrets in source).

### Step 3: `extract-3-draft`

- **Outcome:** Template-shaped draft produced.
- **Done when:** All template sections filled or gaps explicitly marked; workflow includes `todo_id` if applicable.

### Step 4: `extract-4-pre-ship`

- **Outcome:** Write gate evaluated when user requested a file.
- **Done when:** If write requested: static script + `pre-ship-checklist.md` run; if chat-only, step marked N/A with reason.

### Step 5: `extract-5-output`

- **Outcome:** Deliverable returned.
- **Done when:** Draft + provenance in chat, or file written only if pre-ship PASSED and path approved.

## Stop

No silent invention of missing business facts—list open questions explicitly.
