# Adhoc mode (urgent / unplanned stages 5–7)

**Audience:** `rr-builder` when `payload.mode: adhoc`. **Thin wrap** over [feature.md](feature.md) — same cohesion pipeline, mint/branch/run contracts, and hard stop at task-validate. **Do not** fork a second stage matrix.

**Intent delta:** **Urgent / unplanned** interrupt bias — one-session optimize; never “docs later.” Still **full** stages 2–4 gates on rr (urgency ≠ skip).

**Not:** planned feature execute (`--feature`); intake/docs authoring (`--intake`); plan-stage [feature-branch.md](feature-branch.md); product Feature delta; full-slice `--slice`.

## Shared contract

**SoT:** [feature.md](feature.md) for preflight → detect → branch ensure → mint → detail → run loop → done-when / non-goals.

Substitute:

| Feature SoT | Adhoc |
|-------------|-------|
| `payload.mode: feature` | `payload.mode: adhoc` |
| `payload.feature.*` | `payload.adhoc.*` |
| `feature_id` (non_rr) | `adhoc_id` |
| Framing: planned surface already absorbed | Framing: interrupt / ship-now; same gates |

## Urgency preflight (before feature.md body)

1. Load `refs/planning/intake.md`; situate; report stage reached / first block.
2. On rr stages **2–4 FAIL** → **stop** (Next Up `--intake` / peer planner SKILL) — do **not** build; do **not** invent Plan truth as task obligations.
3. On PASS (or `non_rr` collapse) → continue [feature.md](feature.md) mint/branch/run with `payload.adhoc` fields.
4. Bias: prefer finishing mint→detail→task-validate in **this** session when unblocked; still never skip challenge/docs.

## Conflicts / NL

Mutually exclusive with `--intake` and `--feature`; incompatible with lane flags and `--slice` / `--next` / `--step` (same as feature).

| NL | Mode |
|----|------|
| “Urgent / unplanned / interrupt / ship this now” | `adhoc` |
| “Implement planned feature X” / PRD id / selected requirement | `feature` (not this file) |
| Idea / coverage / docs unclear | `intake` |

## Done-when / non-goals

Inherit [feature.md](feature.md). Additional non-goal: treating urgency as license to skip stages 2–4 or invent `docs/rr/` in non_rr.
