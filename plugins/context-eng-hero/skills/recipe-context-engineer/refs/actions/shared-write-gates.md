# Shared write gates (internal)

Used by **create**, **fix**, **redesign**, **design**, **extract** (file write), and **improve** (combined apply draft) after **draft** content exists (in memory, scratch, or off-path mirror)—**not** after silent mutation of the final approved path. Each action's gates step runs these four gates in order (**improve** runs them once on the merged fix+redesign draft).

## Ref index (Read at gate)

| Ref | When |
|-----|------|
| `ui-brand.md` | Static gate (liveness) |
| `pre-write-reflection.md` | Pre-write reflection gate |
| `pre-ship-checklist.md` | Pre-ship gate |
| `gate-prompts.md` | Write gate (approve-revise-abort) |
| Type rubric in `rubrics/<type>.rubric.md` | Pre-write reflection gate only |
| `helper-cli.md` | Improve: render reflection / touch-list inventory |

Record **draft hash** (path + content fingerprint) when static PASSes. Pre-ship 1.1 reuses that result—do not re-run `audit_static.py` unless the draft changed after static.

## Gate order

1. **Static gate**
2. **Pre-write reflection gate**
3. **Pre-ship gate**
4. **Write gate**

## Static gate

- **Outcome:** Static checks pass on **draft** content (scratch mirror)—not a premature “already shipped” target.
- **Liveness:** Emit `◆ Running static audit (~5–10s)…` per `ui-brand.md` before the shell call.
- **Done when:** From plugin root, after PyYAML bootstrap if needed (plugin root `CLAUDE.md` **Python runtime**), `python3 scripts/audit_static.py . <relative-path>` run against the draft under audit; all static rows PASS or fixes applied until PASS. Store output + draft hash. If script missing or errors after bootstrap: **STATIC SKIPPED** with reason—**do not promote** until static PASS or user accepts draft-only.
- **Improve:** Prefer auditing files under `.ai/learning/ce-improve/<run-id>/draft/` (or an isolated overlay plugin_root) when present; map results to intended target relatives in the AskQuestion packet. **Do not** treat a filesystem snapshot of live targets as the goal of this gate—snapshot is optional only if needed later to restore or to finalize the improve **touch list**.

## Pre-write reflection gate

- **Outcome:** Judgment + harness self-audit passed on draft.
- **Done when:** `pre-write-reflection.md` executed; reflection block per `templates/pre-write-reflection.template.md` shows **PASSED**; prefer persisting via lean JSON (`templates/reports/reflection.schema.json`) + `scripts/render_ce_report.py reflection` when the hosting action is **improve** (exit 2 → fix JSON, re-run); any FAIL → revise draft and re-run from **Static gate** (do not promote).

## Pre-ship gate

- **Outcome:** Binary pre-ship checklist verified.
- **Done when:** `pre-ship-checklist.md` run; pre-ship 1.1 reuses last STATIC PASS on same draft hash. Any FAIL blocks promote. Judgment depth is owned by reflection—not re-scored here.

## Write gate

- **Outcome:** Final artifact delivered or blocked.
- **Done when:** If static, reflection, and pre-ship all PASSED: run **approve-revise-abort** AskQuestion per `gate-prompts.md`.
  - **Packet (required before AskQuestion):** lean patch summary + reflection one-liner + links to any diagnosis/apply-plan/draft files that exist for this action (improve: Reports + `apply-plan.md` + draft dir + `touch-list.txt`). Missing required improve links → do not ask; repair packet first.
  - **Approve** → promote draft → approved target path(s); emit patch + reflection summaries.
    - **Improve only:** After promote, ensure `touch-list.txt` lists every repo-relative path just written (inventory for close narrative). Leave paths **unstaged** — default dirty `git status`. **Never** `git add` / `git commit` / `git add -A`.
  - **Request changes** → revise draft; re-run gates from **Static gate**; targets stay at pre-promote state.
  - **Abort** → **no promote**; discard scratch draft / restore only if an optional restore intermediary exists; **prior target disk state unchanged**.
- If any prior gate FAILED: `PRE-WRITE REFLECTION FAILED` or `PRE-SHIP FAILED` as appropriate; prior target disk state unchanged unless user wants draft-only.

## Stop (all hosting actions)

- Do **not** treat “draft already written to the final path” as Approve.
- On Abort, targets must match pre-draft state.
- Improve: filesystem snapshot is **not** a success criterion; after Approve promote, leave touch-list paths **unstaged** (never `git add`).
