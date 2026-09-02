# Shared write gates (internal)

Used by **create**, **fix**, **redesign**, **design**, and **extract** (file write) after draft content exists at an approved plugin-relative path. Each action's `*-4-gates` step runs these four gates in order.

## Ref index (Read at gate)

| Ref | When |
|-----|------|
| `ui-brand.md` | Static gate (liveness) |
| `pre-write-reflection.md` | Pre-write reflection gate |
| `pre-ship-checklist.md` | Pre-ship gate |
| `gate-prompts.md` | Write gate (approve-revise-abort) |
| Type rubric in `rubrics/<type>.rubric.md` | Pre-write reflection gate only |

Record **draft hash** (path + content fingerprint) when static PASSes. Pre-ship 1.1 reuses that result—do not re-run `audit_static.py` unless the draft changed after static.

## Gate order

1. **Static gate**
2. **Pre-write reflection gate**
3. **Pre-ship gate**
4. **Write gate**

## Static gate

- **Outcome:** Static checks pass on revised content.
- **Liveness:** Emit `◆ Running static audit (~5–10s)…` per `ui-brand.md` before the shell call.
- **Done when:** From plugin root, after PyYAML bootstrap if needed (plugin root `CLAUDE.md` **Python runtime**), `python3 scripts/audit_static.py . <relative-path>` run; all static rows PASS or fixes applied until PASS. Store output + draft hash. If script missing or errors after bootstrap: **STATIC SKIPPED** with reason—**do not write** until static PASS or user accepts draft-only.

## Pre-write reflection gate

- **Outcome:** Judgment + harness self-audit passed on draft.
- **Done when:** `pre-write-reflection.md` executed; reflection block per `templates/pre-write-reflection.template.md` shows **PASSED**; any FAIL → revise draft and re-run from **Static gate** (do not write).

## Pre-ship gate

- **Outcome:** Binary pre-ship checklist verified.
- **Done when:** `pre-ship-checklist.md` run; pre-ship 1.1 reuses last STATIC PASS on same draft hash. Any FAIL blocks write. Judgment depth is owned by reflection—not re-scored here.

## Write gate

- **Outcome:** Final artifact delivered or blocked.
- **Done when:** If static, reflection, and pre-ship all PASSED: run **approve-revise-abort** AskQuestion per `gate-prompts.md`; on Approve → patch summary + reflection summary + write to approved path; on Request changes → revise and re-run from **Static gate**; on Abort → no write. If any prior gate FAILED: `PRE-WRITE REFLECTION FAILED` or `PRE-SHIP FAILED` as appropriate; prior disk state unchanged unless user wants draft-only.
