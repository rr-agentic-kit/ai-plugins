# Gate Prompt Patterns

Reusable **AskQuestion** patterns for Context Engineer orchestration. Checkpoint box format: `refs/ui-brand.md`.

**Delivery:** Prefer AskQuestion for these patterns; always fall back to the same options as numbered/labeled prose when the tool or harness is unavailable — see `questioning.md` **Delivery channels**. Do not stall or claim the tool is “unavailable” as product truth.

## Rules

- `header` max 12 characters
- `multiSelect` always `false`
- 2–4 options per prompt; always include a freeform escape ("Other" / "Something else")
- If user types freeform instead of selecting, map intent and continue—do not re-ask the same gate
- One gate at a time; do not stack multiple AskQuestion calls in one turn unless the first answer requires a follow-up
- Text-mode delivery of a gate still counts as that gate; route maps below apply unchanged

---

## Pattern: action-routing

Skill intake when action is unclear (ambient invoke or vague request).

- **question:** "What do you want to do with this artifact?"
- **header:** "Action"
- **options:** Audit it | Improve it | Create new | Something else
- **Route map:**
  - Audit it → **audit** (freeform may pick **audit-redesign** for improvement-only diagnosis)
  - Improve it → **improve** (requires declared path)
  - Create new → **create**
  - Something else → infer from freeform (fix, redesign, extract, test, diff, learn, audit-redesign, design assist) or one clarifying question; if outcome change unclear for edits, run **fix-vs-redesign** first

---

## Pattern: skill-ux-delivery

Create/design clarify for skills—after invoke mode, before draft. Interaction shape only; not Purpose/Procedure content.

- **question:** "How should this skill take input and deliver results?"
- **header:** "Skill UX"
- **options:** Gates + reports | Text-first | Minimal clarify | Other
- **Route map:**
  - **Gates + reports** → Prefer AskQuestion for forks; mandatory text-mode same options (**Delivery channels** in `questioning.md`); staged report/close. Draft README **UX → Clarify/Close** + SKILL **Orchestration** / Execution rules accordingly.
  - **Text-first** → Prose clarify by default; optional AskQuestion when tool present. Still document Delivery channels if any enumerable gate appears.
  - **Minimal clarify** → Open asks / assumptions; no gate graph. If draft has no enumerable forks: one-line N/A (“no AskQuestion gates”) so audit can PASS. If a fork appears later: document Delivery channels.
  - **Other** → Freeform escape; map intent; store as open question or custom shape note—do not invent Purpose/Procedure content.
- Never rewrite Purpose / When / Procedure from this gate alone.

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

## Pattern: post-audit-redesign-routing

After audit-redesign report is emitted.

- **question:** "Improvement report ready. What next?"
- **header:** "Next"
- **options:** Absorb via fix | Absorb via redesign | Done for now
- **Route map:**
  - Absorb via fix → **fix** (pass ranked `absorb: fix` ids + path; skip defer/low)
  - Absorb via redesign → **redesign** (pass ranked `absorb: redesign` ids + path)
  - Done for now → end with **Next Up** block only; no further action

Freeform may request **improve** (full parallel + gated apply) or compliance **audit** instead.

---

## Pattern: post-improve-routing

After improve completes (gates passed and file written, diagnosis-only with empty apply list, or user declined write).

- **question:** "Improve complete. What next?"
- **header:** "Next"
- **options:** Audit again | Run behavior test | Done for now
- **Route map:**
  - Audit again → **audit**
  - Run behavior test → **test**
  - Done for now → end with **Next Up** block only

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
  - Incorporate now → **fix** if all approved topics preserve outcome; **redesign** if any topic changes outcome/audience/capabilities; pass user-project `LEARN-HANDOVER.*` (or chat handover) as failure/delta source; edit **plugin source** only
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
