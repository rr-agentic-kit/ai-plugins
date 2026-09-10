<ui_patterns>

Visual patterns for user-facing Context Engineer output. Orchestrators @-reference this file.

## Stage Banners

Use for major action transitions. Banner rules are **26** `━` characters wide.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━
 CE ► {STAGE NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Stage names (uppercase):**
- `CLASSIFY`
- `AUDIT`
- `FIX`
- `CREATE`
- `EXTRACT`
- `REDESIGN`
- `LEARN`
- `TEST`
- `DIFF`
- `DESIGN`
- `COMPLETE ✓`

Long stage names stay on one line when they fit; otherwise abbreviate or wrap the title on a second line **without** extending the `━` rules.

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
◆ Running static audit (5–10s)…
```

Adjust duration hint to match the operation. Always use the `◆` prefix.

---

## Next Up Block

After each action completes, show what the skill will do next—**no slash copy-paste required**. The skill proceeds via **AskQuestion** or continues directly when the user already chose. Separators are **31** `─` characters wide.

```
───────────────────────────────

## ▶ Next Up

**{action id}: {name}** — {one-line description}

{What happens when the user picks an option—or that you will continue after their answer}

───────────────────────────────

**Also available:**
- {alternative 1} — description
- {alternative 2} — description

───────────────────────────────
```

Gate option labels come from `gate-prompts.md`; do not invent slash commands as the only path forward.

---

## Checkpoint Boxes

User decision required. **31-character** inner width between `║` borders.

```
╔═══════════════════════════════╗
║  CHECKPOINT: {Type}║
╚═══════════════════════════════╝

{Content}

───────────────────────────────
→ {ACTION PROMPT}
───────────────────────────────
```

**Types:**
- `CHECKPOINT: Decision Required` → AskQuestion per `gate-prompts.md`
- `CHECKPOINT: Verification Required` → confirm before write (wraps to two header lines when needed; see Line wrapping)

---

## Line wrapping

Wrap all prose inside checkpoint boxes, Next Up blocks, and liveness messages at **31 characters** (checkpoint inner width).

1. **Wrap all prose** at 31 characters. Stage banner title lines stay one line when possible; long names abbreviate or wrap on a second line without extending the `━` rules.
2. **Break at word boundaries** when possible; break long paths, IDs, or tokens mid-token only when unavoidable.
3. **Never pad** lines with trailing spaces to fill box width — uneven right edges are correct.
4. **Multi-line checkpoint `{Content}`:** each line ≤ 31 characters; use a blank line between paragraphs when needed.
5. **Long checkpoint headers:** when the type label exceeds 31 characters (e.g. `CHECKPOINT: Verification Required`), wrap the label across two lines inside the box; do not widen the `═` rules.

**Worked example — wrapped checkpoint body:**

```
╔═══════════════════════════════╗
║  CHECKPOINT: Decision Required║
╚═══════════════════════════════╝

Approve writes to 3 files
under skills/recipe-context-
engineer/refs/actions/.

───────────────────────────────
→ Choose an option below
───────────────────────────────
```

**Worked example — wrapped checkpoint header:**

```
╔═══════════════════════════════╗
║  CHECKPOINT: Verification║
║  Required║
╚═══════════════════════════════╝

Confirm before applying
changes to plugin.json.

───────────────────────────────
→ Reply to continue or cancel
───────────────────────────────
```

---

## Anti-Patterns

- Varying box/banner widths
- Mixing banner styles (`===`, `---`, `***`)
- Skipping `CE ►` prefix in banners
- Silent shell calls without liveness signal
- Ending with "run `/context-engineer-*`" instead of **Next Up** + gate
- Random emoji (`🚀`, `✨`, `💫`)
- Single lines longer than inner width (31 characters)
- Trailing space padding to align box edges
- Extending `━`/`─`/`═` rules to match long text on one line

</ui_patterns>
