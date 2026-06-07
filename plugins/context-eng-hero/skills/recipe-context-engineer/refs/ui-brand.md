<ui_patterns>

Visual patterns for user-facing Context Engineer output. Orchestrators @-reference this file.

## Stage Banners

Use for major action transitions.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 CE ► {STAGE NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Stage names (uppercase):**
- `CLASSIFY`
- `AUDIT`
- `FIX`
- `CREATE`
- `EXTRACT`
- `REDESIGN`
- `TEST`
- `DIFF`
- `DESIGN`
- `COMPLETE ✓`

---

## Status Symbols

```
✓  Complete / Passed / Verified
✗  Failed / Missing / Blocked
◆  In Progress
○  Pending
⚠  Warning
```

---

## Liveness Signal

Emit **before** shell calls or other silent work so users know the session is alive.

```
◆ Running static audit (~5–10s)…
```

Adjust duration hint to match the operation. Always use the `◆` prefix.

---

## Next Up Block

After each action completes, show what the skill will do next—**no slash copy-paste required**. The skill proceeds via **AskQuestion** or continues directly when the user already chose.

```
───────────────────────────────────────────────────────────────

## ▶ Next Up

**{action id}: {name}** — {one-line description}

{What happens when the user picks an option—or that you will continue after their answer}

───────────────────────────────────────────────────────────────

**Also available:**
- {alternative 1} — description
- {alternative 2} — description

───────────────────────────────────────────────────────────────
```

Gate option labels come from `gate-prompts.md`; do not invent slash commands as the only path forward.

---

## Checkpoint Boxes

User decision required. 62-character inner width.

```
╔══════════════════════════════════════════════════════════════╗
║  CHECKPOINT: {Type}                                          ║
╚══════════════════════════════════════════════════════════════╝

{Content}

──────────────────────────────────────────────────────────────
→ {ACTION PROMPT}
──────────────────────────────────────────────────────────────
```

**Types:**
- `CHECKPOINT: Decision Required` → AskQuestion per `gate-prompts.md`
- `CHECKPOINT: Verification Required` → confirm before write

---

## Anti-Patterns

- Varying box/banner widths
- Mixing banner styles (`===`, `---`, `***`)
- Skipping `CE ►` prefix in banners
- Silent shell calls without liveness signal
- Ending with "run `/context-engineer-*`" instead of **Next Up** + gate
- Random emoji (`🚀`, `✨`, `💫`)

</ui_patterns>
