# Action: learn (internal)

Package an evidence-backed gap list from a **live run miss** (failure **or** friction) on an **existing** skill. Never edits the target skill definition—absorb via **fix** or **redesign**.

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `learn-1-bind` |
| `questioning.md` | `learn-1-bind` |
| `learn-intake.md` | `learn-1-bind` |
| `ui-brand.md` | `learn-1-bind` (banner) |
| Target `SKILL.md` + named action refs | `learn-2-investigate` (effort bar) |
| Sibling README (if present) | `learn-2-investigate` — When/What mismatch only |
| `templates/learn-topics.template.md` | `learn-3-topics` |
| `gate-prompts.md` | `learn-3-topics` (**approve-learn-topics**), `learn-5-close` |
| `templates/learn-handover.template.md` | `learn-4-handover` |
| `close-contract.md` | `learn-5-close` |

## Steps

### Step 1: `learn-1-bind`

- **Outcome:** Target skill and miss source are bound.
- **Done when:** Target skill path resolved; miss source = this chat’s run (default) and/or user problem statement per `learn-intake.md`; optional problem-statement overlay noted; banner `CE ► LEARN` per `ui-brand.md`.

### Step 2: `learn-2-investigate`

- **Outcome:** Gaps classified against on-disk procedure—not chat vibes alone.
- **Done when:** Effort bar below completed (including **behavior curiosity** + **genericness** filter); manual interventions and run-friction signals mapped to procedure loci; each candidate classified `skill_gap` \| `preference_oneoff` \| `env_tool` \| `already_covered`.

### Step 3: `learn-3-topics`

- **Outcome:** Capped topics report ready for human gate.
- **Done when:** Topics report emitted from `templates/learn-topics.template.md` (≤7 topics; only `skill_gap` default-selected); **approve-learn-topics** gate (approve / edit / drop / abort).

### Step 4: `learn-4-handover`

- **Outcome:** Lean handover from **approved** topics only.
- **Done when:** Handover filled from `templates/learn-handover.template.md`; write `LEARN-HANDOVER.md` beside target `SKILL.md`. If path not writable → chat-only draft + one path AskQuestion; then stop or write to user path. No full chat paste.

### Step 5: `learn-5-close`

- **Outcome:** User routed to absorb or stop.
- **Done when:** **post-learn-routing** per `gate-prompts.md` → Incorporate now (fix or redesign per handover hint) \| Revise topics \| Done.

## Investigation effort bar (hard rules)

1. Resolve and Read the target `SKILL.md` (and sibling README if present for When/What mismatch only).
2. For the action(s) that failed or showed friction: Read every ref named in that action’s Ref index (and SKILL Ref index entries those steps require). Do **not** skim SKILL alone.
3. Reconstruct intended step sequence vs chat: what the agent skipped, invented, or what the human patched.
4. **Behavior curiosity (tool/read budget):** Reconstruct which Reads/tools the procedure forced vs what the agent actually did—over-read, serial where Ref index co-names peers, round-trips that one step could batch. Candidate absorb shapes: `batch` (parallel tool/Task coalesce in procedure step text), `read-budget` (fewer staged Loads / merge co-named refs into one step instruction), or existing `step` / `stop-rule` / `ref` when procedure text is the locus. Point absorb at procedure step text / Ref index—do **not** teach slash-command chaining (`chat-orchestration.md`).
5. **Genericness gate:** Ask “Would this change help the next project with different domain files?” No → `preference_oneoff`. Yes + procedure locus → `skill_gap`.
6. Drop `already_covered` and default-deselect `preference_oneoff` / `env_tool` (still list under Auto-dropped).
7. Cap **7** topics; merge related gaps; each topic needs evidence + skill locus + absorb shape (`step` \| `stop-rule` \| `ref` \| `anti-trigger` \| `probe` \| `readme-when` \| `batch` \| `read-budget`).

## Stop

- Learn **never** edits the target skill definition.
- No bible-sized handover: target + miss + approved table + non-goals + fix-vs-redesign hint only.
- No live run evidence (and no problem statement) → wrong action (use audit/fix). Painful-but-“successful” runs still count as live run evidence.
- Creating a new artifact → **create** / **extract**, not learn.
