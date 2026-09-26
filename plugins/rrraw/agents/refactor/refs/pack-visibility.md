# Pack: visibility (phase 6)

**Band:** `visibility` · **Phase:** 6 · **Mandatory LLM + call-site Grep** (no tool substitute)

## Load (only if not already in session)

1. `skills/s-coder/refs/code.principles.md` § Visibility / encapsulation
2. `skills/s-coder/refs/compliance-rubric.md` — **CP031**
3. Stack language refs when known (modifier vocabulary)

## Procedure

1. For each type / method / field / nested type / export in scoped production files: note current visibility
2. **Grep** consumers outside the candidate tighter boundary
3. Emit when a tighter level is safe; cite **CP031**
4. Phase 6 **only narrows** — unused deletion is Phase **7**

## Disposition (required)

| Value | When |
|-------|------|
| `fix` | All proven callers inside tighter boundary (same type → private; same package/module → package-private / no-export / `internal` / unexported / `pub(crate)`); compile-time only; do **not** delete symbols |
| `clarify` | Borderline (e.g. same-module tests in another package; unclear multi-module layout) |
| `escalate_human` | Published API, SPI, reflection/serialization, framework DI, multi-artifact outside scope, or uncertain external use — never silent-narrow |

## Checklist

- [ ] Call-site evidence before `fix`
- [ ] Empty array valid only after a real LLM + Grep pass

## Output shape

`{file, line, phase: 6, type: "visibility", description, disposition}`
