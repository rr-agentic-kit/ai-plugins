# output-formats

**Owner:** Doc file naming, markdown cascade docs, JSON internals (`items.json`, `session-state.json`), durable `status.yaml` / `agent.plan.md` / `future.md`, and append-only Q&A history.

**Load when:** After compose (cascade docs already on disk); skill persist of `session-state.json` / `status.yaml` / `raw-history/` / notes; first compose (emit `agent.plan.md`); first Q&A.

Item records: [doc-standards/item-schema.md](doc-standards/item-schema.md). Schema: [schemas/items.schema.json](schemas/items.schema.json). Track/patch/pins: [baselines.md](baselines.md). Injection: [agent-config.md](agent-config.md).

## Layout

Cascade docs write to `payload.output_dir` (Discover default `{PROJECT_ROOT}/docs/discovery/`; Plan default `{PROJECT_ROOT}/docs/plan/`; next-track → `{phase}/{next}/`). Root **always** keeps `rrr-status.yaml`, `agent.plan.md`, `future.md`, `tech.md`, and `later.md` in `{PROJECT_ROOT}/docs/` — never a second `lines.yaml`. Reject writing operational detail (`levels`, digests, `challenge`, `mint_hash`) into `rrr-status.yaml`.

```
{PROJECT_ROOT}/docs/
  rrr-status.yaml                 # SUMMARY — phase/track/product/docs glance (not pin input)
  agent.plan.md                   # non-patch tripwire (skill-owned; not cascade input)
  future.md / tech.md / later.md  # parking (not validator input)
  discovery/
    status.yaml                   # DETAIL — ES/MRD/BRD revs/pins/challenge/mint_hash
    session-state.json
    executive-summary.md
    mrd.md
    brd.md
    business-case.yaml            # Discover→Plan hard gate (skill-owned; not cascade stem)
    assumptions.md                # conditional
    opportunity-tree.md           # conditional
    interview-synthesis.md        # conditional
    pretotype-brief.md            # conditional
    *.notes.yaml
    items.json
    decision-ledger.yaml
    *.challenge.report.md
    raw-history/
    0.2/                          # only once next opens
  plan/
    status.yaml                   # DETAIL — PRD
    session-state.json
    prd.md
    research-report.md
    prd.notes.yaml
    items.json
    decision-ledger.yaml
    prd.challenge.report.md
    raw-history/
    0.2/
```

| Doc type | Filename |
|----------|----------|
| executive-summary | `discovery/executive-summary.md` |
| mrd | `discovery/mrd.md` |
| brd | `discovery/brd.md` |
| prd | `plan/prd.md` |
| business-case handoff | `discovery/business-case.yaml` (machine; Discover freeze; Plan entry gate; **skip humanize**) |
| assumptions map | `discovery/assumptions.md` (conditional; humanize) |
| opportunity tree | `discovery/opportunity-tree.md` (conditional; humanize) |
| interview synthesis | `discovery/interview-synthesis.md` (conditional; humanize) |
| pretotype brief | `discovery/pretotype-brief.md` (conditional; humanize) |
| summary status | `rrr-status.yaml` (YAML; skill-owned; **not** pin/digest input) |
| phase baseline status | `{discovery\|plan}/status.yaml` (YAML; skill-owned; validator input — mechanical codes only) |
| version tripwire | `agent.plan.md` (skill-owned; **not** validator cascade input; pairing SoT is this skill) |
| future inbox | `future.md` (**not** validator input; no ids; no SEMVER) |
| tech capture | `tech.md` (**not** validator input; no ids; no gates; passive append-only) |
| later parking lot | `later.md` (**not** validator input; no ids; passive; distinct from `{level}.notes.yaml`) |
| off-level notes | `{level}.notes.yaml` under the phase dir (always YAML; same write/load/delete for every level; exists only while unresolved) |
| item graph | `{phase}/items.json` (always JSON) |
| decision ledger | `{phase}/decision-ledger.yaml` (always YAML; skill-owned; validator input) |
| session checkpoint | `{phase}/session-state.json` (always JSON) |
| Q&A history | `{phase}/raw-history/{UTC compact ISO-8601}.yaml` |
| research report | `plan/research-report.md` |
| challenge report | `{phase}/{stem}.challenge.report.md` (one per cascade doc; overwrite on each scan of that stem) |

Create `--output-dir` if it does not exist. Create `raw-history/` on first Q&A. Create `{level}.notes.yaml` on first off-level note for that doc — even if the composed `{level}.md` does not exist yet. File exists only while unresolved notes remain; skill deletes it when empty after compose persist. Create `{phase}/{next}/` only when the skill mints `next` after confirm.

`--format` allowed value is `md` only. `yaml` and `json` → `UNSUPPORTED_FORMAT` ([input-resolution.md](../../skills/rr-discovery/refs/input-resolution.md)). `payload.format` stays `"md"`. `items.json` and `session-state.json` are always JSON. `decision-ledger.yaml` and phase `status.yaml` are always YAML — skill-owned, validator input, not selected by `--format`. `{level}.notes.yaml` is always YAML — not selected by `--format`, not an item, **not validator input**. `future.md`, `agent.plan.md`, `tech.md`, `later.md`, and `rrr-status.yaml` are **not validator cascade input** — do not parse them as cascade docs. Cascade `{stem}.yaml` is stale input for `--rewrite`, not a live format. Do not write `planning-bundle.json`, `session-log.md`, or `lines.yaml`. `decisions.json` is not a user artifact; decisions live in `session-state.json`. Reason-graph bodies live in `decision-ledger.yaml`, not the decision log.

## Markdown doc format

Each composed doc file. Frontmatter is `track` + `doc_rev` + `pins` — not stub `version: 1` / `traces_from` ([baselines.md](baselines.md)):

```markdown
---
doc_type: prd
track: "0.1"
doc_rev: 2
pins:
  brd: { rev: 2, digest: "sha256:..." }
created: 2026-06-24T10:00:00Z
---

# PRD: [Title]

[doc content from compose agent — item headings + `_key_:` line + `>` body per item-schema]

## Item index

| ID | Parent | Spec | MoSCoW |
|----|--------|------|--------|
| PRD-3 | BRD-2 | draft | — |
| PRD-3.1 | PRD-3 | ready | Must |
```

ES `pins: {}`. Unfrozen `doc_rev: "?"`. Index column 4 is the level’s native field (`MoSCoW` / `Kano` / `Class`). Heading + `_key_:` metadata are a closed vocabulary — parser is regex, not an LLM. Item templates: [doc-standards/item-schema.md](doc-standards/item-schema.md).

## `items.json`

Compose merges this file on every invocation (read-modify-write: replace only this `doc`’s records; do not clobber other levels). Must match md `_key_:` headers; drift is a validator FAIL. Graph checks (parent walk, numbering, spec/status) run on this file. Skill reads it after compose to refresh `item_registry` — never copies item records through chat.

```json
{
  "items": [
    {
      "id": "PRD-3.1",
      "parent": "PRD-3",
      "kind": "leaf",
      "spec": "ready",
      "priority_method": "moscow",
      "moscow": "Must",
      "rationale": "r-014",
      "title": "Guest checkout",
      "doc": "prd"
    }
  ]
}
```

## Raw-history YAML

Verbatim Q&A only. Decisions and assumptions stay in `session-state.json`. Append after **every** Q&A round (discovery, compose clarifications, stage-exit blind-spots). Pause still leaves reanalyzable history.

Filename: UTC compact ISO-8601 (`YYYY-MM-DDTHHMMSSZ.yaml`), e.g. `2026-08-15T185203Z.yaml`. One file per session. `--resume` appends to `session-state.raw_history_path`.

```yaml
session:
  started: 2026-08-15T18:52:03Z
  action: discover
  output_dir: /abs/path/docs/discovery
  question_mode: ask
  depth: standard
turns:
  - ts: 2026-08-15T18:53:01Z
    level: executive-summary
    source: discovery
    question:
      id: q-001
      text: Who feels this pain?
      mode: ask
      options:
        - Engineering managers
        - ICs
        - Both equally
    answer:
      text: Engineering managers
      selected:
        - Engineering managers
```

| Field | Notes |
|-------|-------|
| `session.started` | ISO-8601 UTC of first Q&A (file create) |
| `session.action` | Normalized `action` |
| `session.output_dir` | Resolved output directory |
| `session.question_mode` | `ask` \| `text` |
| `session.depth` | `shallow` \| `standard` \| `deep` |
| `turns[].ts` | ISO-8601 UTC of the answer |
| `turns[].level` | Cascade level or `session` |
| `turns[].source` | `discovery` \| `compose` \| `blind-spots` \| `research` \| `challenge` \| `presave` \| `panel` |
| `turns[].question` | `id`, `text`, `mode`, `options[]` |
| `turns[].answer` | `text` (verbatim), `selected` (option labels when applicable) |

Append-only: never rewrite prior turns. Create `raw-history/` on first Q&A. If the session file is missing on resume, create a new timestamped file and update `raw_history_path`.

## `rrr-status.yaml` + phase `status.yaml`

Summary + detail. Skill-only writers. Schema and mint rules: [baselines.md](baselines.md). Summary lives in `{PROJECT_ROOT}/docs/`; detail in `{PROJECT_ROOT}/docs/{discovery|plan}/` even when cascade docs fork to `{phase}/{next}/`.

On first `--setup` / first compose: mint summary defaults + phase detail (`track: "0.1"`, `product`/`docs` as `0.1.0?`, `next: null`, phase stems `rev: "?"`, `challenge: {}`, `next_challenge: {}`, `claude_config_version` from [agent-config.md](agent-config.md), phase `mint_hash` computed). On freeze / lock-target / confirmed major-minor: mint phase detail per baselines, recompute `mint_hash`, refresh summary (`phase`, `discovery_complete`, `summary` line). After compose persist: dirty that doc’s `challenge.status` when it was `clean-shallow`, `clean-deep`, or `dirty-accepted`. After challenge persist: stamp per-doc `challenge:` from findings. Compose never writes these files. Scripts never increment `track`. `challenge` is not a validator FAIL.

Validator input for mechanical codes only (`PARENT_UNFROZEN`, `STALE_PIN`, `REV_WHILE_OPEN`, `HAND_BUMP`) — **phase detail only**. Plan validation loads Discovery status for parent BRD pins. Summary is not pin input.

## `agent.plan.md`

Always-on tripwire: refuse non-patch version work and protect the root load line. Pairing policy is this skill ([baselines.md](baselines.md)), not this file. Body template: [agent.plan.md](agent.plan.md) (version + load line: [agent-config.md](agent-config.md)). Skill emits/overwrites on first compose, `--setup`, and when `injection.version` advances. **Not** validator cascade input. Lives at `{PROJECT_ROOT}/docs/agent.plan.md`.

Resolve sync (idempotent): append the locked load line to existing root SoT files (`CLAUDE.md`, `AGENTS.md`, and any new root agent SoT). Restore if stripped. Do not create missing SoT files. Do not rewrite their bodies. Set `rrr-status.yaml.claude_config_version`.

```bash
sh scripts/validate_planning.sh --sync-agent-config --repo-root <PROJECT_ROOT> --docs-root <PROJECT_ROOT>/docs
```

## `future.md`

One inbox at `{PROJECT_ROOT}/docs/future.md`. Create on first parked beyond-current note that has **no** owning track yet. **Not validator input.** No item ids. No SEMVER. Meeting residue / no go-nogo.

| Rule | |
|------|--|
| Never auto-promote | Opening next **offers** to promote matching sections; user confirms each. |
| Next track already open | Do **not** duplicate into `future.md`. Notes for that track go to `{level}.notes.yaml` under `{phase}/{next}/`. |
| What belongs here | Unassigned, or beyond-next (past the one open next track). |

Rejected: `future/` folder; per-track future files; treating this file as a cascade doc.

## `tech.md`

One file at `{PROJECT_ROOT}/docs/tech.md`. Same tier as `later.md` / `future.md`. Create on first mechanism-level append. **Not validator input.** No item ids, no gates, never composed into cascade docs.

| Rule | |
|------|--|
| Passive | Skill appends freely when mechanism-level detail surfaces (shalls, AC, integration points, NFR mechanism, error-handling specifics, requirement-explosion overflow). No periodic maintenance; rr-planner does not re-read it on later passes. |
| Not cascade | Never mint item ids; never run Gates 1–7 against this file. |

## `later.md`

One global file at `{PROJECT_ROOT}/docs/later.md`. Create on first user-deferred topic. **Not validator input.** No item ids.

| Rule | |
|------|--|
| Passive | Skill writes freely when the user defers a topic ("discuss later"). No periodic maintenance; no auto-incorporate. |
| Distinct from notes | `{level}.notes.yaml` is active/addressed-then-deleted for off-level answers on a specific doc. `later.md` is a global parking lot. |

## Challenge report (per-doc worklist)

One file per cascade stem: `{output_dir}/{stem}.challenge.report.md` (e.g. `executive-summary.challenge.report.md`). Overwrite **only that stem's file** on each challenge persist for that doc — latest scan replaces that doc's worklist; addressed = absent from that file. Do not keep finding-id history or `open_ids` in `status.yaml` (per-run `bs-001` is not stable). Each finding’s `doc` stem drives per-doc `challenge.status` and Address-now routing; keep `doc_ref` for humans. Skill persists from findings JSON; the challenge agent does not write it. Stamp `depth: shallow | deep` in frontmatter (must match `status.yaml` `challenge.<stem>.depth`).

Challenge runs exactly one doc per invocation. Parallel address switches docs but processes one report at a time.

```markdown
---
doc: executive-summary
depth: deep
scanned_digest: "sha256:..."
---

# Challenge: executive-summary

[findings worklist for this stem only]
```

## Session checkpoint (`session-state.json`)

Written on **every stop** and after **each level completion**. Required for `--resume`. Internal only — not a human plan doc and **not** project knowledge (`status.yaml` is).

```json
{
  "metadata": {
    "action": "discover",
    "depth": "standard",
    "question_mode": "ask",
    "format": "md",
    "output_dir": "{PROJECT_ROOT}/docs/discovery/",
    "raw_history_path": "raw-history/2026-08-15T185203Z.yaml",
    "updated": "ISO-8601"
  },
  "checkpoint": {
    "status": "paused|in_progress|complete|blocked",
    "current_level": "brd",
    "pending_clarifications": [],
    "levels_completed": ["executive-summary", "mrd"]
  },
  "decisions": [],
  "assumptions": [],
  "level_facts": {},
  "composed_docs": {
    "executive-summary": "executive-summary.md",
    "mrd": "mrd.md"
  },
  "item_registry": {},
  "frozen_levels": ["executive-summary", "mrd"],
  "discovery_complete": false,
  "project_posture": {},
  "preferences": {
    "questions_per_cycle": 1
  },
  "viability_stale": {
    "executive-summary": false,
    "mrd": false
  },
  "viability": [
    {
      "level": "executive-summary",
      "verdict": "proceed",
      "conditions": [],
      "dissent": [],
      "binding": true
    }
  ],
  "note_sessions": {}
}
```

`raw_history_path` is relative to `output_dir`. Resume loads this file, continues from `checkpoint.current_level`, and appends Q&A to that history file.

`composed_docs`: `doc_type` → path relative to `output_dir`. Paths only — never document bodies. Do not stash compose output in session-state; compose writes immediately.

`item_registry`: id → `{ doc, parent, kind, spec, class? }`. Skill refreshes this from `items.json` after compose. Resume uses it for minting. Frozen re-compose remap of child `parent:` is compose’s job in the same invocation.

`project_posture`: `{}` until confirm; then the Session field in [project-posture.md](../../skills/rr-planner/refs/project-posture.md). Resume skips the posture gate when `user_confirmed` is true and uncontradicted.

`preferences.questions_per_cycle`: max AskQuestion count per address cycle (default `1`). Set via `--questions-per-cycle N` ([input-resolution.md](../../skills/rr-planner/refs/input-resolution.md)); confirm-once persistence.

`viability_stale`: per binding level (`executive-summary`, `mrd`). Set `true` when compose changes load-bearing ES facts ([baselines.md](baselines.md)). Gate 7 re-sit clears it.

`viability[]`: Gate 7 / premise-test verdicts ([expert-panel.md](../../skills/rr-planner/refs/expert-panel.md)). Binding at executive-summary and MRD.

`discovery_complete`: `true` after Discover writes a valid `business-case.yaml` and freezes BRD ([business-case-handoff](../../skills/rr-discovery/refs/business-case-handoff.md)). Plan refuses entry without frozen BRD + handoff.

`note_sessions`: per-level index of parked notes; body is `{level}.notes.yaml` ([note-sessions.md](../../skills/rr-planner/refs/note-sessions.md)). Drop the key when that sidecar is deleted. Sidecars are not `--format` docs and are not parsed by `validate_planning.sh`.

Skill owns `decision-ledger.yaml` ([decision-ledger.md](decision-ledger.md)). Compose and challenge never write it. Validator loads it when present.

## `business-case.yaml`

Discover skill-owned machine handoff after BRD freeze. Field contract: [business-case-handoff.md](../../skills/rr-discovery/refs/business-case-handoff.md). **Skip humanize.** Not a cascade stem — validator may check presence/required keys for Plan entry fixtures; does not participate in item graph.

## Cascade prose persist

After compose agent draft: orchestrating skill runs [compose-prose.md](../../skills/rr-discovery/refs/compose-prose.md) (`rr-humanize` generate/rewrite + scan) before treating cascade `.md` as final. Same gate for Plan PRD and conditional session markdown artifacts.

## Status merge

| Source | `final_status` |
|--------|----------------|
| All levels `ok`, success-criteria pass (static script + judgment); queue empty; no binding `hold`/`kill`; no `viability_stale`; challenge all `clean-shallow`, `clean-deep`, or `dirty-accepted` | `ok` |
| User stopped mid-session, accepted partial gaps, or leftover challenge `dirty` (not accepted) at chain exit | `partial` |
| Binding `hold`, unresolved `kill`, or open re-decision queue | `blocked` |
| Input-resolution error or unrecoverable agent failure | `failed` |

## Adapter rules

1. Overwrite confirm: [cascade.md](../../skills/rr-planner/refs/cascade.md) per-level discovery step 8. Skip the prompt when `--input` implied refresh.
2. Always write `session-state.json` on stop or level completion for resume (include `raw_history_path`, `project_posture` once confirmed, `viability[]`, `note_sessions`, `composed_docs` paths). Skill is the only writer of this file. Skill is also the only writer of `decision-ledger.yaml`, `status.yaml`, `agent.plan.md`, and `future.md`.
3. Compose writes/merges `items.json`. Skill reads it; skill does not write it. Compose reads `reserved_ids` from the ledger and never re-mints those ids. Compose writes frontmatter `track` / `doc_rev` / `pins`; skill mints `status.yaml` after freeze.
4. Append a raw-history turn after every Q&A; do not wait for stage-exit. Skill owns `raw-history/`.
5. Write/append `{level}.notes.yaml` when an off-level answer is parked; do not put parked prose in item headings. Skill owns sidecars; prune: [note-sessions.md](../../skills/rr-planner/refs/note-sessions.md). Next-track notes while `next` is open go to that track's sidecar, not `future.md`.
6. Research and challenge reports are standalone `.md` files, not merged into cascade docs. Skill persists those reports from findings JSON. Challenge overwrites `{stem}.challenge.report.md` for the challenged stem only (worklist, not history).
7. Compose writes human cascade docs (`{level}.md` only). Document bodies never travel through chat. Research/challenge still return findings JSON. Compose does not write `status.yaml` / `agent.plan.md` / `future.md`. After compose persist, the skill dirties that doc’s `challenge.status` when it was `clean-shallow`, `clean-deep`, or `dirty-accepted`.
8. After compose Task: parse slim receipt → if clarifications, ask and re-invoke → else read `items.json` to refresh `item_registry` → Gate 3 static ([success-criteria.md](success-criteria.md)). FAIL blocks `final_status: ok`. Sidecars, `future.md`, and `agent.plan.md` are not validator input.
9. Pause skips pre-save ([proactivity.md](../../skills/rr-planner/refs/proactivity.md)). Freeze is a `frozen_levels` update plus a docs-patch mint in phase `status.yaml` (+ summary refresh), not a second write of the doc ([cascade.md](../../skills/rr-planner/refs/cascade.md), [baselines.md](baselines.md)).
10. First compose: write phase `status.yaml`, refresh `rrr-status.yaml`, emit `docs/agent.plan.md`, sync the one-liner on existing root SoT, set `claude_config_version` ([agent-config.md](agent-config.md)).
