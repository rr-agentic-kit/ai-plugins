# File paths

All career artifacts live in `~/career/`. Create the directory during preflight if missing.

## Directory structure

```
~/career/
├── {Name}_Master_Resume.md
├── {Name}_Master_CoverLetter_Components.md
├── applications/
│   └── {Company}_{RoleFocus}_{Date}/
│       ├── {Name}_Resume_{RoleFocus}_{Company}_{Date}.md
│       ├── {Name}_CoverLetter_{Company}_{Date}.md
│       ├── jd.txt                    # optional: pasted JD archive
│       └── t10-mapping.md            # optional: requirement mapping artifact
└── archive/                          # optional: superseded versions
```

## Naming conventions

| Artifact | Pattern | Example |
|----------|---------|---------|
| Master resume | `{Name}_Master_Resume.md` | `Jane_Doe_Master_Resume.md` |
| Master cover components | `{Name}_Master_CoverLetter_Components.md` | `Jane_Doe_Master_CoverLetter_Components.md` |
| Tailored resume | `{Name}_Resume_{RoleFocus}_{Company}_{Date}.md` | `Jane_Doe_Resume_StaffPlatform_Stripe_2026-06-07.md` |
| Tailored cover letter | `{Name}_CoverLetter_{Company}_{Date}.md` | `Jane_Doe_CoverLetter_Stripe_2026-06-07.md` |
| PDF export (user) | `{FirstName}-{LastName}-{Role}.pdf` | `Jane-Doe-Staff-Platform.pdf` |

**Date format:** `YYYY-MM-DD` in filenames.

**RoleFocus:** Short slug from locked role variant (e.g., `StaffPlatform`, `AIEngineer`, `MLEngineer`, `Hybrid`).

## Preflight checks

1. `~/career/` exists — create if not
2. For tailor paths: master resume exists at expected path (or user provides inline)
3. For tailor cover: tailored resume + master cover components exist
4. Never write outside `~/career/` without explicit user consent

## confirm-before-write

Before writing any file:

1. Show target path and artifact type
2. Summarize what will be written (sections, word count for cover)
3. User confirms or requests edits
4. Write only after confirmation

## Version management

- Master documents: update in place; optional copy to `archive/` with date suffix before major rewrites
- Tailored documents: one folder per application under `applications/`
- Quarterly master review: user updates master; skill does not auto-schedule
