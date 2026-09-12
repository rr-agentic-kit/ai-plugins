# Close contract (dual surface)

Load at orchestration step 6 and action close steps.

## Predicate

| Invoke surface | Close behaviour |
|----------------|-----------------|
| **Skill** (`Read` SKILL or parent Action) | **AskQuestion** or **Next Up** (`ui-brand.md`); follow-ups are **verb-only**—no `/slash` strings |
| **Command** (user picked a slash) | May name the next slash as **user homework**; never claim the agent will chain commands |

Platform: commands cannot execute other commands (`chat-orchestration.md`).

## Verb-only follow-ups (shared templates)

| State | User follow-up |
|-------|----------------|
| Audit PASS | Ship, or run behavior test if unverified |
| Audit FAIL | Fix every FAIL in this report |
| Test probe FAIL (same contract) | Fix using probe ids from this report |
| Test FAIL (wrong outcome/capability) | Redesign |
| After create / fix / redesign write | Audit again, run behavior test, or done |
| After redesign write | Re-audit the same path |
| After learn handover | Incorporate with this handover (fix or redesign per hint), revise topics, or done |
| After absorb from learn handover | Delete user-project `LEARN-HANDOVER.*` (not cache); re-audit / re-test on **plugin source** |

## Action close steps

| Action | Close |
|--------|-------|
| create, fix, redesign | Matching `post-*-routing` gate or **Next Up** |
| extract (file write) | Same as create |
| extract (chat-only) | Provenance + optional **Next Up**; no write gates |
| learn | **post-learn-routing** or **Next Up**; verb-only: Incorporate with this handover |
| audit, test, diff | `post-*-routing` or **Next Up** only |
| design | Shared write gates; **Next Up** if no post-design gate |

After close: if the user picks a follow-on, re-enter **Act**—do not defer to slash copy-paste.
