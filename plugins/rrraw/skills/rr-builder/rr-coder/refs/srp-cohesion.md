# SRP / cohesion checklist (CP023 / CP015)

Classify types with **red / green / gray**, then for **gray** apply **new vs live** disposition. Do **not** treat “≥2 domains” as an automatic fail.

## Zones

| Zone | When | Verdict |
|------|------|---------|
| **Red** | Clear domain god-object / fat **CP015** method (cohesion) — **Phase 4** finding | Finding + **`disposition: fix`** (collapse / extract) |
| **Green** | Small class, **one** clear domain, readable, no duplicated product API | No finding — do not invent an SRP split |
| **Gray** | Small class that **repeats the same job** (compat forks / near-duplicate paths) | Apply **new vs live** below |

**Size / fan-out only** (>300 LOC, high coupling) is **Phase 3** (`god_class`) — do **not** re-emit as Phase 4 cohesion red. Phase **4** covers fat **CP015** / gray dual-API only.

**Hints only (not automatic fails):** `*Issuer` + repository inject; `save` then `sign` on a **single** path. Use them to look for gray duplication, not to force a split.

## Gray disposition (new vs live)

| Context | How to detect | Disposition |
|---------|---------------|-------------|
| **New** | In review/refactor **target** as added/changed; branch introducing the type; no/few callers in mainline yet | **`fix`** — prefer quality from the start (collapse fork / one API). Cheap now. |
| **Already live** | Stable path, many callers, shipped behavior, compat methods exist for a reason | **`clarify`** (why-comment / ownership note) and/or **`escalate_human`** (tradeoff: maintain cost vs risk). Do **not** silent big-bang refactor. |

Disposition values: `fix` | `clarify` | `escalate_human`. Required on every **Phase 4** finding.

## Rule mapping

- Red size / fan-out → **CP023** via **Phase 3** (`god_class`)
- Gray duplication or cohesion red → **CP023** via **Phase 4** (`mixed_responsibility`)
- Fat service method (validate + domain + persist + events) → **CP015**; small-type forks → **CP023**

## Anti-patterns (model)

- Do **not** treat “≥2 domains named in docs” as red.
- Do **not** auto-fix **live** gray when risk/clarity tradeoff is unclear — escalate or clarify.
- Docs that assign “A and B” alone do not create a red finding. Docs + gray dual API on **new** code → still **`fix`**. Docs + gray dual API on **live** code → clarify/escalate, not drive-by rewrite.
