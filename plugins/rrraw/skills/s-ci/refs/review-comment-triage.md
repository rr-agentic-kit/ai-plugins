# PR/MR comment triage

Same evidence bar for human and bot/AI comments — never auto-apply unverified bot suggestions.

## Outcome constraints

| Condition | Action |
|-----------|--------|
| Validity **and** chosen fix both **High** (`IN_SCOPE`) | Implement (`APPLY_AS_PROPOSED` or `BETTER_ALTERNATIVE`), test, push; reply with commit |
| `FALSE_POSITIVE` at High | Reply with evidence only; **do not** resolve thread |
| `OUT_OF_SCOPE` at High | Reply with out-of-scope template; no code; no thread resolve; offer issue link when available |
| Any gate Medium/Low, or `UNCLEAR` after one pass | Batch `ASK_USER` (do not interrupt mid-loop) |
| Pure taste nit with no standards win | `DECLINE` — do not ask |

**Strict autonomy:** auto-act only when High on both “claim is real” and “chosen fix is right.” Otherwise investigate once → batch ask.

## Once per run

Derive a one-line **task boundary** from PR/MR title, summary (above `---`), and linked ticket (`gh pr view` / `glab mr view`). Example: *"Add retry logic to payment webhook handler."* Gate scope against this boundary for every comment.

## Gates (per comment)

| Gate | Question | Outputs |
|------|----------|---------|
| **1 Validity** | Is the claim true here? | `REAL` / `FALSE_POSITIVE` / `UNCLEAR` |
| **1b Scope** (only if `REAL`) | Belongs in *this* PR/MR? | `IN_SCOPE` / `OUT_OF_SCOPE` / `FOLLOW_UP` |
| **2 Solution** (only if `IN_SCOPE`) | Is the fix (or best fix) correct? | `APPLY_AS_PROPOSED` / `BETTER_ALTERNATIVE` / `DECLINE` / `ASK_USER` |

Evidence: read anchored code + mitigations; check callers in **PR/MR-changed files**; treat proposed fixes as hypotheses.

| Confidence | Validity | Solution |
|------------|----------|----------|
| **High** | Confirmed in context; mitigations checked | One clear fix matching project patterns |
| **Medium / Low** | Incomplete or speculative | Multiple plausible fixes or unclear direction |

## Batch ask triggers

- Gate 1 `UNCLEAR` after one investigation
- Scope `OUT_OF_SCOPE` / `FOLLOW_UP` at Medium/Low
- Two+ plausible fixes; pattern conflict; material scope expansion

Pipeline SAST / dependency / secrets findings → escalate to org scanner / security skill; do not locally “fix” SAST without that path. Prose security claims in threads → triage first; escalate scanner only if `REAL`.

## Optional reply skeletons

**Implemented:** `Addressed in [commit]. [what changed]`

**Better alt:** `Applied [alt] instead of suggested because [reason]. See [commit].`

**False positive:** `After checking [context], not an issue because [evidence]. Leaving thread open.`

**Out of scope:** `Outside this PR/MR scope. Tracking in #[n] if created.`

**Decline:** `Not changing because [reason].`

**Batch ask (to user):** list each thread with options A/B/C + recommendation.
