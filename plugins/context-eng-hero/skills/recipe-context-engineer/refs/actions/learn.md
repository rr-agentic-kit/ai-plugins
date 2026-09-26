# Action: learn (internal)

Package an evidence-backed gap list from a **live run miss** (failure **or** friction) on an **existing** skill. Never edits the target skill definition—absorb via **fix** or **redesign**.

## Drive

| Mode | Behaviour |
|------|-----------|
| **interactive** (default) | AskQuestion when bind overlays need choice; after handover, **post-learn-routing** |
| **`--auto`** | No AskQuestion for bind overlays when stated defaults apply; approve/skip every remaining learn AskQuestion so steps 1→5 run straight through; after handover, **Next Up** only (skip **post-learn-routing**). Does **not** auto-start fix/redesign |

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `learn-1-bind` |
| `questioning.md` | `learn-1-bind` |
| `learn-intake.md` | `learn-1-bind` |
| `ui-brand.md` | `learn-1-bind` (banner); `learn-5-close` (Next Up under `--auto`) |
| Target `SKILL.md` + named action refs | `learn-2-investigate` (effort bar) |
| Sibling README (if present) | `learn-2-investigate` — When/What mismatch only |
| `templates/learn-topics.template.md` | `learn-3-topics` (build/input — **not** chat-emit) |
| `templates/learn-handover.template.md` | `learn-4-handover` |
| `gate-prompts.md` | `learn-5-close` (**post-learn-routing**; skip under `--auto`) |
| `close-contract.md` | `learn-5-close` |

## Steps

### Step 1: `learn-1-bind`

- **Outcome:** Target skill and miss source are bound; **three path roles** resolved per `learn-intake.md`.
- **Done when:** (1) **Read-from** path = readable `SKILL.md` (source or cache OK **read-only** for investigation); (2) **Write-handover** path = **user project** (`docs/rr/LEARN-HANDOVER.<skill>.md` when `docs/rr/` exists, else project-root); (3) **Absorb-into** path = **plugin source** checkout only (never `~/.claude/plugins/cache/**` or other installed runtime copies); (4) miss source = this chat’s run (default) and/or user problem statement; banner `CE ► LEARN` per `ui-brand.md`. If absorb-into unclear → AskQuestion once (source path / describe location) — under `--auto`, bind with stated defaults when signals present; unresolvable source still stops (see Stop).

### Step 2: `learn-2-investigate`

- **Outcome:** Gaps classified against on-disk procedure—not chat vibes alone.
- **Done when:** Effort bar below completed (including **eager behavior curiosity** inventory + five probes, **genericness**, **layer-split**, and **mechanism-completeness**); economy inventory + probe answers recorded before classification completes; manual interventions and run-friction signals mapped to procedure loci; each candidate classified `skill_gap` \| `preference_oneoff` \| `env_tool` \| `already_covered`. When the Ref index co-names peers for a step under investigation, **Read them in one parallel turn** (same absorb shape learn recommends via `batch`).

### Step 3: `learn-3-topics`

- **Outcome:** Internal topic package ready for handover (not a human gate).
- **Done when:** Topics built from `templates/learn-topics.template.md` (≤7 topics; only `skill_gap` default-selected); **adequacy probe** satisfied or gaps added/dropped with reason (see effort bar §10); **no** full-report chat-emit; **no** approve gate; proceed to step 4.

### Step 4: `learn-4-handover`

- **Outcome:** Lean handover from **default-selected `skill_gap`** topics only, written in the **user project**.
- **Done when:** Handover filled from `templates/learn-handover.template.md`; write under the **user project** (prefer `docs/rr/LEARN-HANDOVER.<skill-name>.md` when `docs/rr/` exists, else project-root `LEARN-HANDOVER.<skill-name>.md`). **Target** + **Incorporate hint** list **absorb-into (plugin source)** paths — not cache. **Stop-rule:** never write handover or absorb edits under `~/.claude/plugins/cache/**` / installed runtime skill trees. If user-project path unwritable → chat-only draft + one path AskQuestion (under `--auto`, state path failure and stop — do not invent a path). No full chat paste.

### Step 5: `learn-5-close`

- **Outcome:** User routed to absorb or stop.
- **Done when:** Interactive → **post-learn-routing** per `gate-prompts.md` → Incorporate now (fix or redesign per handover hint) \| Revise topics \| Done. Under `--auto` → write handover, then **Next Up** only (no **post-learn-routing** AskQuestion).

## Investigation effort bar (hard rules)

1. Resolve and Read the target `SKILL.md` (and sibling README if present for When/What mismatch only).
2. For the action(s) that failed or showed friction: Read every ref named in that action’s Ref index (and SKILL Ref index entries those steps require). Do **not** skim SKILL alone.
3. Reconstruct intended step sequence vs chat: what the agent skipped, invented, or what the human patched.
4. **Layer-split (founder/human corrections):** Before merging into topics, split multi-clause corrections into layers — (1) **outcome/success**, (2) **standing mechanism/reflex**, (3) **persistence/session**, (4) **stop-rule/anti-trigger**. Each non-empty layer → a candidate topic **or** an Auto-dropped row with explicit reason. Do **not** collapse a mechanism layer into Purpose/README prose alone.
5. **Eager behavior curiosity (tool/read economy) — hard gate, no silent skip:** From the **missed run** / problem statement (not extra skill Reads), inventory first, then answer all five probes. Inventory: tools used; files Read. Probes: (1) What tools did the chat use? (2) What files did it read? (3) Necessary? (4) Fewer tokens? (5) Fewer interactions? Then either a `skill_gap` with `batch` / `read-budget` / `script` (or related `step` / `stop-rule` when procedure text is the locus) **or** an Auto-dropped `already_covered` / `preference_oneoff` row stating “economy: no gap” + reason. Candidate absorb shapes: `batch` (parallel tool/Task coalesce in procedure step text), `read-budget` (fewer staged Loads / merge co-named refs into one step instruction), `script` (same fetch/filter/id-keyed write every time — add or index a helper under `scripts/` per `helper-cli.md` **When to add**; stdout = fields the next step needs, not raw API dumps). Point absorb at procedure step text / Ref index—do **not** teach slash-command chaining (`chat-orchestration.md`). **Learn’s own investigate:** when Ref index co-names peers for a step, Read them in one parallel turn.
6. **Genericness gate:** Ask “Would this change help the next project with different domain files?” No → `preference_oneoff`. Yes + procedure locus → `skill_gap`.
7. Drop `already_covered` and default-deselect `preference_oneoff` / `env_tool` (still list under Auto-dropped).
8. **Mechanism-completeness:** For each `skill_gap` that changes outcome, success metric, north-star, or Purpose language, require a companion absorb that forces runtime behavior (`step` \| `stop-rule` \| `probe` \| `anti-trigger`) — or mark the topic incomplete and add the companion. Purpose/README-only is **not** enough unless Auto-dropped states “prose-only OK” + reason.
9. Cap **7** topics; merge related gaps; each topic needs evidence + skill locus + absorb shape (`step` \| `stop-rule` \| `ref` \| `anti-trigger` \| `probe` \| `readme-when` \| `batch` \| `read-budget` \| `script`). **Anti-trigger:** when under the cap, prefer dropping a duplicate outcome row over dropping the **only** mechanism companion (`step`/`probe`/`stop-rule`/`anti-trigger`/`script`) for an outcome/redesign topic.
10. **Adequacy probe (before handover write):** Ask once — “Would absorb of *only* these selected topics still miss an operational nuance the founder/human named?” If yes → add a topic or list under Auto-dropped with reason. Do not present a philosophy-only package as complete. If founder/human named waste/friction (tools, Reads, tokens, interactions) and selected topics omit economy (`batch` / `read-budget` or Auto-dropped “economy: no gap”), **fail adequacy**.

## Stop

- Learn **never** edits the target skill definition (absorb via **fix** / **redesign** on **plugin source** only).
- Learn **never** writes into runtime/cache/installed skill copies — handover → **user project**; absorb → **source**.
- **`--auto` never invents absorb-into**; unresolvable source still stops.
- No bible-sized handover: target + miss + approved table + non-goals + fix-vs-redesign hint only — **but** lean must not erase mechanism layers (effort bar §4, §8, §9).
- No live run evidence (and no problem statement) → wrong action (use audit/fix). Painful-but-“successful” runs still count as live run evidence.
- Creating a new artifact → **create** / **extract**, not learn.
