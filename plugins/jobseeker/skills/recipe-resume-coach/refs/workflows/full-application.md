# Workflow E — Full application

End-to-end: tailor resume then tailor cover letter.

**Prerequisite:** Master resume + JD

**Input:** Master resume, JD, company name, role variant

**Output:** Tailored resume + tailored cover letter in `~/career/applications/{Company}_{RoleFocus}_{Date}/`

## TodoWrite step ids

```
full-preflight
full-resume
full-cover
full-review
full-write-confirm
```

## Steps

### full-preflight

1. Verify master resume exists
2. Lock role variant
3. Create application folder: `~/career/applications/{Company}_{RoleFocus}_{Date}/`
4. Archive JD as `jd.txt` (optional)

### full-resume

Execute `workflows/tailor-resume.md` in full:

- T1 → T2 → **T10** → transform → optimize → gates 1–5
- Produce tailored resume in application folder
- Retain T10 mapping for cover gap step

**Do not proceed to cover until resume gates PASS.**

### full-cover

Execute `workflows/tailor-cover.md` in full:

- Use tailored resume (not master) as input
- Address T10 gaps honestly in cover
- Gate 6 must PASS

### full-review

Final checklist before user exports PDFs:

- [ ] Resume gates 1–5 PASS
- [ ] Cover gate 6 PASS
- [ ] T10 mapping archived
- [ ] User confirmed all metrics
- [ ] File names match `file-paths.md` conventions

### full-write-confirm

1. Summarize both artifacts and paths
2. PDF export guidance: export from Word/Google Docs/LaTeX — not scanned image
3. Suggested PDF names: `{FirstName}-{LastName}-{Role}.pdf`
4. Close: track application response rate; quarterly master review
