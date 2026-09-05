# req-smell

**Owner:** Linguistic anti-patterns checklist for requirements and WWAS AC before slice freeze.

**Load when:** `ac-smell` todo; pre-freeze gate; challenge targeting AC.

**Does not:** Replace product judgment. Does not author test code. Fail freeze until cleaned or explicit hold.

## WWAS shape (required)

Acceptance = **Why** / **What** / observable **Acceptance** — product pass/fail. No sprint-sizing language.

## Smell checklist (fail until fixed or hold)

| Smell | Fail example | Clean direction |
|-------|--------------|-----------------|
| Vague verbs | “support”, “handle”, “enable”, “seamless” | Observable action + outcome |
| Loopholes | “as appropriate”, “where possible”, “etc.” | Closed condition or explicit non-goal |
| Passive voice | “errors are handled” | Who/what system does what |
| Open-ended lists | “including but not limited to…” | Finite enumerated set or deferred status |
| Incomplete conditionals | “If X…” with no else / timeout | Full branch or non-goal |
| Unobservable AC | “user is happy” | Measurable or inspectable signal |
| Mechanism-as-AC | “use Redis lock” | Product outcome; mechanism → delta/spine |
| Sprint ceremony | “fits in one sprint” | Slice / phase language only |

## Gate behavior

1. Scan selected requirement leaves + AC for the slice.
2. Any smell → block freeze **or** record explicit `hold` assumption with user confirm.
3. Challenge may re-run this checklist ([challenge-method.md](challenge-method.md)).

## Done-when

- Zero open smells on freeze candidates, or documented holds
- WWAS shape present on freeze-bound AC
