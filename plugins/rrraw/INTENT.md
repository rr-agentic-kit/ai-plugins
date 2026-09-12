# RRRaw (rrraw)

Flag-driven **Discover → Plan → (Execute)** freeze chain that owns process and quality so humans own product judgment — plus an orthogonal test path.

## Why

Meta-dev frameworks fail when humans become process owners: freeze-by-say-so with open quality debt, smell-clean mistaken for challenge, ceremony Next-Up that incentivizes skip, and Plan-only self-challenge while Discover stays gate theater. RRRaw exists so skills own next step, quality layers, version impact, and challenge cadence — and so the builder→objective likelihood rises, not the wiki.

**Done when:** Across Discover and Plan, the skill drives advance/freeze/challenge; the user confirms product calls and explicit risk acceptance; artifacts stay instruments of revenue and cheap change.

## What

Cross-skill spine: **rr-discovery** (ES→MRD→BRD → `business-case.yaml`) → **rr-planner** (PRD+ / spine / slice → `execute-slice.yaml`) → future Execute. Side path: **rr-test** (test excellence; no planning versions). Shared runtime law lives under `refs/planning/` (baselines, challenge layers, progress).

**Out of scope:** Company process replacement; stuffing Spec into the plugin overview README; rr-test challenge-layer ownership.

## When

### Use when

- Proving a bet before Plan, then planning a buildable slice from a frozen case
- Needing mechanical freeze/pins plus layered scrutiny without human process memory
- Running orthogonal test excellence beside the spine

### Avoid when

- Ambient “review the repo” with no Discover/Plan/test intent
- Expecting the human to remember freeze gates, challenge cadence, or version fan-out
- Treating plugin `README.md` as Spec (that file is overview/install only)

## Philosophy

- **Proactive deduction over interrogation** — infer and propose; ceremony questions are failure
- **Automation over ceremony** — freeze, pins, impact fan-out are skill-owned
- **Goal over artifact ceremony** — docs/code serve revenue and cheap change; section coverage is not done
- **Layered scrutiny** — auto-reflection → smells → `--challenge` (standard) → `--challenge deep`; smell-clean ≠ challenged
- **Backward-chain** — when the current level cannot support the real goal given parents, challenge **upstream** (Discover: MRD↔ES, BRD↔MRD; Plan: Plan→Discover reopen) — do not bury as HOLD

## UX

Canonical **User is not process-owner** contract for the plugin. Skill READMEs link here; they keep invoke chrome local.

### Invoke

Skills via flags or clear NL. No slash-command process. Bare invoke never silent-rediscovers or silent-composes past entry gates.

### Intake

Status-first (`rrr-status.yaml` → phase `status.yaml` + session-state). Skill classifies action and emits payload before body work.

### Clarify

AskQuestion for product judgment, binding holds, entry-gate fail, and **risk acceptance** — not for “which ceremony step next.” Cap `questions_per_cycle`. Assumption auto-close: one plausible alternative → skill may close with recorded reasoning; two+ peers → AskQuestion required.

### Output

Cascade/standing docs + machine handoffs; challenge reports only for standard/deep layers; auto-reflection is one-line / session — no fourth report format. Smells stay inline / gate tables.

### Close

Skill owns **Next Up**. Do not incentivize skip (“just move on” as freeze escape). Advance-without-finishing is allowed when the skill judges a **solid subset** load-bearing-stable — skill auto-marks downstream impact on upstream change. **Freeze mint** still requires frozen parents (`PARENT_UNFROZEN`). Skill may **auto-suggest freeze** only after **standard** challenge is clear for load-bearing stems **or** explicit **risk-accept** (AskQuestion → `dirty-accepted` stamp). Quality veto: refuse freeze-by-user-say-so over open quality debt.

## Constraints

Facts that regenerate shared law + skill Specs:

- Challenge layers SoT: `refs/planning/challenge-layers.md` (auto-reflection / smells / standard / deep)
- Version + freeze mint SoT: `refs/planning/baselines.md` — mint independent of attestation for CI; skill auto-suggest freeze requires standard-clear or risk-accept
- Work advance on draft upstream allowed for cited solid subset; full parent freeze required to **mint** frozen child
- Attestation map: standard → `clean-shallow`; deep → `clean-deep`; risk-accept → `dirty-accepted` (validator may still see legacy `clean` — docs own the mode map)
- Process-ownership UX SoT = this file’s **UX**; do not restate essay in plugin README or skill READMEs
- rr-test is a side path in When/Avoid only — out of challenge-layer scope unless later smell reuse

## Notes

- Install / quick start / skills table: [README.md](README.md)
- Per-skill Spec: `skills/rr-discovery/README.md`, `skills/rr-planner/README.md`, `skills/rr-test/README.md`
- Runtime: `refs/planning/` + skill `refs/`
