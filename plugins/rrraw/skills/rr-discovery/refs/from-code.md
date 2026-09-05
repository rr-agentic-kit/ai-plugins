# from-code

**Owner:** Reverse Discover path — research the codebase, compose ES→MRD→BRD stems, mark `maturity: code-extraction`. Not interview-driven discover.

**Load when:** `action: from-code` (`--from-code` or NL reverse-from-code). Skill-owned research + existing compose — **no** new Task agent.

**Does not:** invent market/TAM/buyer/ICP from package names; auto-freeze / mint `business-case.yaml`; run a polish interview; code-review the product; compose Plan PRD.

## Intent

| Path | Seed | Outcome maturity |
|------|------|------------------|
| `--discover` (default) | Interview / AskQuestion cascade | `idea` → `draft` as today |
| `--from-code` | Codebase research + reflection | Compose → **`code-extraction`**; later shape → **`draft`** |

Incomplete reverse is expected. Improve quality after reverse with `--challenge` or `--resume` / continue shaping — not a long remaining-questions gauntlet.

## Research checklist (Discover-scoped)

Thorough pass under Discover scope only. `--input` may name a research root (directory); default `PROJECT_ROOT`.

| Look for | Capture |
|----------|---------|
| What shipped | Modules, entrypoints, user-facing surfaces, README claims that match code |
| Who it serves (if inferable) | Actors in UI/API/docs — **not** invented ICP personas |
| Problem signals | Issues, TODOs, error domains, support paths, domain language in code |
| Constraints | Auth, tenancy, compliance hooks, hard limits visible in code/config |
| Domain language | Terms the codebase already uses — prefer those over marketing gloss |

Reflect before compose:

1. Outcome vs mechanism — park mechanism in `tech.md`; Discover owns problem/market/viability framing.
2. Discover vs Plan — features, RICE, stories → notes / Plan; do not mint PRD here.
3. Best framing of the bet given evidence — weak sections stay thin or `hold`.

Persist findings in `session_state.from_code_evidence` (`refs/planning/output-formats.md`). Cite that evidence in inheritance / compose facts where helpful.

## Weak-OK policy

- Do **not** invent TAM, buyer, ICP, beachhead, or competitive set from package/folder names.
- Leave thin sections thin; prefer explicit `hold` / `vague` over fake precision.
- Items minted this pass: default `spec: idea` (item enum unchanged — maturity is **doc-level** only).
- Empty research tree → stop (deterministic). User abort → checkpoint and stop.

## Contradiction-only clarification

Ask only when something **blocks a coherent stem**:

| Ask | Leave thin / hold |
|-----|-------------------|
| Mutually exclusive readings of the same shipped behavior | Missing market sizing / ICP polish |
| Facts that contradict across README vs code vs config | “Make this great” completeness gaps |
| Blocking `domain_context` / posture fields that cannot be inferred without inventing | Nice-to-have section depth |

Cap stays `preferences.questions_per_cycle`. Merge **only** contradiction items into `checkpoint.pending_clarifications`. Do not expand into a discovery interview.

## Compose + maturity

1. Skip ideation ([ideation.md](ideation.md)). Depth still trims which stems are written ([input-resolution.md](input-resolution.md)).
2. Run posture inventory path ([project-posture.md](project-posture.md)) — seed `existing`; confirm + `domain_context` only for contradictory / missing blocking fields.
3. Compose Discover stems via existing compose `Task` + [compose-prose.md](compose-prose.md).
4. Stamp each composed stem **`maturity: code-extraction`** in cascade frontmatter **and** mirror on `status.yaml` `levels.<stem>.maturity`.
5. Drain contradiction queue (or hold explicitly). **Stop** — keep `code-extraction`. Do **not** freeze; do **not** mint `business-case.yaml` while any composed stem is still `code-extraction`.

Challenge remains a separate primary (`--challenge`) — not part of the from-code `chain`.

## Promote to draft

On user continue-shaping / `--resume` that edits content toward normal Discover work (past “accept reverse as-is”):

1. Set stem `maturity: draft` (frontmatter + status mirror).
2. Clear from-code special-casing for that stem.
3. Enter normal Discover gates / freeze path — origin no longer matters.

Accepting reverse as-is without shaping leaves maturity at `code-extraction` (freeze still blocked).

## Done-when / Stop

**Done when:**

- Discover stems in `cascade_levels` written with `maturity: code-extraction`
- `from_code_evidence` persisted
- Contradiction queue drained or explicitly held
- Session checkpoint written; **no** freeze / handoff

**Stop when:** empty research tree; user abort; existing stems present and user refuses overwrite (`ask` route — no silent overwrite).

## Non-goals

- Code review, tickets, implementation advice
- Plan PRD / RICE / stories (`rr-planner`)
- Polish interview to “complete” reverse docs
- Auto-promotion to `ready` or freeze from reverse alone
- `rr-planner --from-code` (separate plan)
