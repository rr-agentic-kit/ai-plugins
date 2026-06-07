# Shared write gates (internal)

Used by **create**, **fix**, **redesign**, and **design assist write** after draft content exists at an approved plugin-relative path. Each action's `*-4-gates` step runs these four gates in order.

## Load (Read)

- `ui-brand.md`
- `gate-prompts.md`
- `pre-write-reflection.md`
- `harness-effectiveness.md`
- `pre-ship-checklist.md`
- Type rubric: `skill.audit-rubric.md` | `command.audit-rubric.md` | `agent.audit-rubric.md` | `rule.audit-rubric.md` | `workflow.audit-rubric.md` (loaded again inside pre-write reflection)

## Gate order

1. **Static gate**
2. **Pre-write reflection gate**
3. **Pre-ship gate**
4. **Write gate**

## Static gate

- **Outcome:** Static checks pass on revised content.
- **Liveness:** Emit `◆ Running static audit (~5–10s)…` per `ui-brand.md` before the shell call.
- **Done when:** From plugin root, after PyYAML bootstrap if needed (see plugin root `CLAUDE.md` **Python runtime**), `python3 scripts/audit_static.py . <relative-path>` run; all static rows PASS or fixes applied until PASS. If script missing or errors after bootstrap, follow `audit.md` (**STATIC SKIPPED** with reason)—do not write until static PASS or user accepts draft-only.

## Pre-write reflection gate

- **Outcome:** Judgment + harness self-audit passed on draft.
- **Done when:** `pre-write-reflection.md` executed; reflection block per `pre-write-reflection.template.md` shows **PASSED**; any FAIL → revise draft and re-run from **Static gate** (do not write).

## Pre-ship gate

- **Outcome:** Binary pre-ship checklist verified.
- **Done when:** `pre-ship-checklist.md` run; any FAIL blocks write. Contract/judgment depth is owned by **Pre-write reflection**—do not re-score rubric ids here; pre-ship covers schema/discovery/safety/orchestration binaries.

## Write gate

- **Outcome:** Final artifact delivered or blocked.
- **Done when:** If static, reflection, and pre-ship all PASSED: run **approve-revise-abort** AskQuestion per `gate-prompts.md`; on Approve → patch summary + **Pre-write reflection** summary + write to approved path; on Request changes → revise and re-run from **Static gate**; on Abort → no write. If any prior gate FAILED: `PRE-WRITE REFLECTION FAILED` or `PRE-SHIP FAILED` as appropriate; prior disk state unchanged unless user wants draft-only.
