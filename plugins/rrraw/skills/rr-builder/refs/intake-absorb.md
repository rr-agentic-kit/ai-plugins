# intake-absorb (builder)

**Audience:** `rr-builder` when `payload.mode: intake`. Wrapper over shared `refs/planning/intake.md`. Prefer continue stages **1→7** in-session when unblocked.

**Does not:** Skip stages 2–6 to reach code; thin-patch Plan docs; `Read` planner `refs/*`; invent `docs/rr/` in non_rr.

## Flow

```
Read refs/planning/intake.md
  → situate (stage 1)
  → if stages 2–4 not PASS: peer-invoke skills/rr-planner/SKILL.md
       with purpose (--intake / --change / --challenge)
       via Task sub-agent OR parent-inline Read SKILL.md + purpose
  → after 2–4 PASS: mint (stage 5) + detail (stage 6)
  → offer/continue --feature (default) or --adhoc (urgent) for stage 7
```

## Stage ownership

| Stage | Builder behavior |
|-------|------------------|
| **1 Situate** | Match class; report stage reached / first block |
| **2–4 Docs / challenge / select** | **Peer planner only** — invoke `skills/rr-planner/SKILL.md` with purpose. Do **not** thin-absorb Plan internals or load planner refs. |
| **5–6 Mint + detail** | After 2–4 PASS — contracts in [feature.md](feature.md) (adhoc wraps same) |
| **7 Code** | Continue into [feature.md](feature.md) or [adhoc.md](adhoc.md) run loop (AskQuestion: `--feature` default \| `--adhoc` if urgent) |

## Peer invoke

When Plan work is needed: **Task** `skills/rr-planner/SKILL.md` **or** parent-inline `Read` that SKILL + purpose payload; let planner Procedure resolve its own refs. Shared law only: `refs/planning/intake.md`.

## Entry bias

Prefer one-session walk when additive and unblocked. On stage-3 judgment → peer planner/discovery; resume intake / `--feature` / `--adhoc` only after return + stages complete.

**non_rr:** collapse to situate → mint → detail → code; never invent `docs/rr/`; no planner peer needed for Plan cascade.

## Next Up

AskQuestion = legal pipeline moves only (`refs/planning/intake.md`). Never “skip docs / skip challenge / code now.”

| Block | Offer |
|-------|-------|
| Docs gap / dual-lens / cohesion | peer `rr-planner` `--intake` / `--change` / `--challenge` |
| Discover reopen | `rr-discovery` |
| Ready 1–6 | continue `--feature` (default) or `--adhoc` (urgent); same session OK |

## Done-when

- Situate + first blocking stage reported
- Either peer-invoked planner before code with clear Next Up, or stages 1–6 PASS and stage 7 started/offered via [feature.md](feature.md) / [adhoc.md](adhoc.md)
- No code while stages 2–6 incomplete on rr
- No builder-owned Plan patching

## Non-goals

- Obligation-only cascade substitute for Plan absorb
- Thin docs absorb that bypasses planner Procedure
- Auto-coding past open challenge/impact
- Slice-validate / delivered on feature/adhoc continuation
