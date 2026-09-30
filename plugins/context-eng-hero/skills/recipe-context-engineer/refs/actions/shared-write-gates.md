# Shared write gates (internal)

Used by **create**, **fix**, **redesign**, **design**, **extract** (file write), and **improve** (combined apply draft) after **draft** content exists **in LLM memory**—**not** after silent mutation of the final approved path. Gates do **not** assume off-path mirrors, a `draft/` tree, or a scratch copy of targets. Each action's gates step runs these four gates in order (**improve** runs them once on the merged fix+redesign draft).

Improve may still persist lean diagnosis files under `.ai/learning/ce-improve/<run-id>/` (reports, apply-plan, optional `reflection.json`)—that is **read-budget / diagnosis scratch**, not an artifact draft tree.

## Ref index (Read at gate)

| Ref | When |
|-----|------|
| `pre-write-reflection.md` | Pre-write reflection gate |
| `pre-ship-checklist.md` | Pre-ship gate |
| `gate-prompts.md` | Write gate (approve-revise-abort) |
| `ui-brand.md` | Static gate (liveness) |
| Type rubric in `rubrics/<type>.rubric.md` | Pre-write reflection gate only |
| `helper-cli.md` | Improve: render reflection / touch-list inventory |

## Gate order

1. **Pre-write reflection gate** (memory)
2. **Pre-ship gate** (memory)
3. **Write gate** — Approve → Write/Edit final paths
4. **Static gate** (post-write verify on written paths)

## Pre-write reflection gate

- **Outcome:** Judgment + harness + **opportunity-clean** self-audit passed on the in-memory draft.
- **Done when:** `pre-write-reflection.md` executed; reflection block per `templates/pre-write-reflection.template.md` shows **PASSED** (judgment + harness + opportunity-clean all PASS); prefer persisting via lean JSON (`templates/reports/reflection.schema.json`) + `scripts/render_ce_report.py reflection` when the hosting action is **improve** (exit 2 → fix JSON, re-run); any FAIL → revise **memory** draft and re-run from **Pre-write reflection gate** (do **not** Write final paths).
- Applies to **all** hosting write actions including **fix** and improve’s combined draft—same craft bar.

## Pre-ship gate

- **Outcome:** Binary pre-ship checklist verified (memory judgment; no hard dependency on a pre-write `audit_static.py` run).
- **Done when:** `pre-ship-checklist.md` run; item **1.1** records that static **will** run on written targets before claiming done (schema/frontmatter checks that do not need the script may still be verified here). Any FAIL blocks Write. Judgment depth is owned by reflection—not re-scored here.

## Write gate

- **Outcome:** Final artifact delivered or blocked.
- **Done when:** If reflection and pre-ship both PASSED: run **approve-revise-abort** AskQuestion per `gate-prompts.md`.
  - **Packet (required before AskQuestion):** lean patch summary + reflection one-liner + links to any diagnosis/apply-plan files that exist for this action (improve: Reports + `apply-plan.md`; optional lean `reflection.json` under report scratch). Missing required improve links → do not ask; repair packet first. Do **not** require a `draft/` dir link.
  - **Approve** → **Write/Edit intended final path(s) only**; emit patch + reflection summaries.
    - **Improve only:** After Write, ensure `touch-list.txt` lists every repo-relative path **actually written** (inventory for close narrative). Leave paths **unstaged** — default dirty `git status`. **Never** `git add` / `git commit` / `git add -A`.
  - **Request changes** → revise **memory** draft; re-run gates from **Pre-write reflection gate**; final paths stay unchanged (no Write this cycle).
  - **Abort** → **no Write** (or restore final paths only if a Write already happened in a prior failed cycle); discard memory draft; **prior target disk state unchanged** unless that restore applies.
- If any prior gate FAILED: `PRE-WRITE REFLECTION FAILED` or `PRE-SHIP FAILED` as appropriate; prior target disk state unchanged unless user wants draft-only in chat.

## Static gate (post-write verify)

- **Outcome:** Static checks PASS on **written** final paths—bytes must be on disk (`audit_static.py` cannot audit memory alone).
- **Liveness:** Emit `◆ Running static audit (~5–10s)…` per `ui-brand.md` before the shell call.
- **Done when:** From plugin root, after PyYAML bootstrap if needed (plugin root `CLAUDE.md` **Python runtime**), `python3 scripts/audit_static.py . <relative-path>` run against each written target; all static rows PASS. On FAIL → Edit the written path + re-static (**cap 2** revision cycles). Only after PASS (or user-accepted draft-only) mark the write action done. If script missing or errors after bootstrap: **STATIC SKIPPED** with reason—**do not claim done** until static PASS or user accepts draft-only.
- **Improve:** Audit the **written** target relatives listed in `touch-list.txt` (and companions the static checks expect: `ACRONYMS.md` + `GLOSSARY.md`, sibling skill packs referenced by links). Map results in the close / AskQuestion packet. Do **not** create a `draft/` overlay for static.

## Stop (all hosting actions)

- Do **not** treat “draft already written to the final path” as Approve.
- On Abort, targets must match pre-Write state (restore only if a prior failed cycle already Wrote).
- Improve: filesystem snapshot / draft tree is **not** a success criterion; after Approve Write, leave touch-list paths **unstaged** (never `git add`). Report scratch under `.ai/learning/ce-improve/<run-id>/` is diagnosis-only—not an artifact overlay.
- **Anti-cheat:** Do **not** treat “run `--improve` / `audit-redesign` next” as opportunity-clean or write-gate satisfaction. Reflection owns opportunity-clean inline; do not spawn improve/opportunity Tasks as a gate substitute.
