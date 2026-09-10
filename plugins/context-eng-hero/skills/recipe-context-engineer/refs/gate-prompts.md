# Gate Prompt Patterns

Reusable **AskQuestion** patterns for Context Engineer orchestration. Checkpoint box format: `refs/ui-brand.md`.

## Rules

- `header` max 12 characters
- `multiSelect` always `false`
- 2–4 options per prompt; always include a freeform escape ("Other" / "Something else")
- If user types freeform instead of selecting, map intent and continue—do not re-ask the same gate
- One gate at a time; do not stack multiple AskQuestion calls in one turn unless the first answer requires a follow-up

---

## Pattern: action-routing

Skill intake when action is unclear (ambient invoke or vague request).

- **question:** "What do you want to do with this artifact?"
- **header:** "Action"
- **options:** Audit it | Fix or improve | Create new | Something else
- **Route map:**
  - Audit it → **audit**
  - Fix or improve → if outcome change unclear, run **fix-vs-redesign** first; else **fix**
  - Create new → **create**
  - Something else → infer from freeform (extract, test, diff, redesign, learn, design assist) or one clarifying question

---

## Pattern: fix-vs-redesign

When user wants changes but scope is ambiguous.

- **question:** "Are you changing what it does (outcome, audience, capabilities)?"
- **header:** "Scope"
- **options:** Wording only | Change outcome | Not sure
- **Route map:**
  - Wording only → **fix**
  - Change outcome → **redesign**
  - Not sure → one sentence each way; re-ask once if still ambiguous, then default **fix** for typos/format, **redesign** for new steps/gates/audience

---

## Pattern: approve-learn-topics

After learn topics report is emitted (`learn-3-topics`).

- **question:** "Approve these learn topics for handover?"
- **header:** "Topics"
- **options:** Approve selected | Edit topics | Abort learn
- **Route map:**
  - Approve selected → **learn-4-handover** with current selection
  - Edit topics → user reselects / drops / rewrites locus; re-emit report; re-ask once
  - Abort learn → no handover write; **Next Up** only

Freeform escape maps to edit (describe override) or abort.

---

## Pattern: approve-revise-abort

Pre-write confirmation after gates pass on draft content.

- **question:** "Approve this draft for write?"
- **header:** "Approve?"
- **options:** Approve | Request changes | Abort
- **Route map:**
  - Approve → write to approved path
  - Request changes → revise draft; re-run gates from static
  - Abort → no write; offer **post-fix-routing** or **post-create-routing** as appropriate

Used by `refs/actions/shared-write-gates.md` **Write gate**.

---

## Pattern: post-audit-routing

After audit report is emitted.

- **question:** "Audit complete. What next?"
- **header:** "Next"
- **options:** Fix failures now | Run behavior test | Done for now
- **Route map:**
  - Fix failures now → **fix** (pass audit report + path)
  - Run behavior test → **test**
  - Done for now → end with **Next Up** block only; no further action

If verdict PASS and user picks fix, confirm they want polish-only (**fix**) vs contract change (**redesign**) via **fix-vs-redesign**.

---

## Pattern: post-fix-routing

After fix completes (gates passed and file written, or user declined write).

- **question:** "Fix complete. What next?"
- **header:** "Next"
- **options:** Audit again | Run behavior test | Done for now
- **Route map:**
  - Audit again → **audit**
  - Run behavior test → **test**
  - Done for now → end with **Next Up** block only

---

## Pattern: post-learn-routing

After learn handover is written (or chat-only draft accepted).

- **question:** "Learn package ready. What next?"
- **header:** "Next"
- **options:** Incorporate now | Revise topics | Done for now
- **Route map:**
  - Incorporate now → **fix** if all approved topics preserve outcome; **redesign** if any topic changes outcome/audience/capabilities; pass `LEARN-HANDOVER.md` (or chat handover) as failure/delta source
  - Revise topics → return to **learn-3-topics**; re-gate **approve-learn-topics**
  - Done for now → end with **Next Up** block only; note handover path if written

---

## Pattern: post-create-routing

After create completes (file written or draft-only).

- **question:** "Artifact created. What next?"
- **header:** "Next"
- **options:** Audit it | Run behavior test | Done for now
- **Route map:**
  - Audit it → **audit**
  - Run behavior test → **test**
  - Done for now → end with **Next Up** block only
