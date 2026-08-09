# ATS formatting

Parse integrity rules for resume Markdown. Gate 4 enforces these.

This skill writes `.md` only. PDF/DOCX export is a downstream user step — structure content so it survives plain-text parse and later export.

## Checklist (before write)

- [ ] Single column flow — no sidebars, tables-as-layout, or text boxes in source
- [ ] Standard section headers: Summary, Experience, Skills, Education, Certifications
- [ ] No icons, skill bars, graphics, or images in Markdown
- [ ] Contact info in document body (not comments/HTML-only blocks)
- [ ] Consistent date format (MM/YYYY or Month YYYY — pick one)
- [ ] Consistent bullet style throughout
- [ ] ~2 pages of content for senior (8+ years) when exported
- [ ] File name per `file-paths.md` (`.md`)
- [ ] Plain-text test: read without formatting — sections detectable, content readable
- [ ] Skills as flat or categorized plain text — not graphics
- [ ] ~20–30% white space target; 3–5 bullets per role

## Export-time notes (user, not this skill)

When the user exports to PDF/DOCX later:

- Standard fonts: Arial, Calibri, Helvetica, Times New Roman (10–12pt body)
- No headers/footers containing critical info only
- File name: `FirstName-LastName-Role.pdf`

## Anti-patterns

| Anti-pattern | Why it fails | Fix |
|--------------|--------------|-----|
| Keyword stuffing | Modern ATS/LLM detect unnatural density | Embed terms in achievement context |
| Skill dumping (40+ items) | Signals lack of focus | 15–20 defensible, categorized |
| "Objective" statement | Near-zero fixation time | One-line positioning statement |
| Creative section labels | Parser + human confusion | Standard headers |
| Tables / multi-column | Parser misattributes content | Single column |
| Unverified metrics | Interview failure | Defensible numbers only |
| Duty bullets | No "so what?" | Convert to XYZ/TEAL/CAR |
| Generic summary | Wastes top-third | JD-specific 3–4 sentences |
| Tutorial projects as lead | Low signal for senior | Production work first |
| Photo (US/UK tech) | ATS noise; bias risk | Omit |

## Structured design for AI parsers

- Explicit sections: Summary, Experience, Skills, Education, Certifications
- Chronological work history with title, company, dates, bullets separated
- Skills as flat list or categorized plain text
- Summary short and factual
- Content order in text flow matters — don't rely on visual layout for meaning

## Evidence block pattern (for LLM rerankers)

Each tailored bullet should map:

```
JD requirement → Action + Method + Metric + Scope
```

**Example (AI Engineer JD: "RAG in production"):**
> Owned production RAG serving 2.4M queries/day; p99 80ms; eval gates (RAGAS + golden set) before release.
