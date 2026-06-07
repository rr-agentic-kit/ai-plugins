# Disambiguation

Consolidates signal handling across `questioning.md`, `gate-prompts.md`, `fix-intake.md`, and `redesign-intake.md`. **Load at Intake** (orchestration step 1).

## Signal classification

| Signal | Definition | Treatment |
|--------|------------|-----------|
| **Missing** | Field not mentioned; no partial signal | `questioning.md` routing; offer paths forward |
| **Ambiguous** | Partial signal; multiple valid interpretations | State assumption inline, proceed — do NOT ask |
| **Contradictory** | Two incompatible signals in same message | Name both → one AskQuestion → unresolved → conservative default + state it |
| **Unclear** | User said something but intent cannot be parsed | Enumerable → AskQuestion; non-enumerable → one open ask, then proceed |

## Default assumption table

When proceeding without asking, state these once inline:

| Field | Default assumption |
|-------|-------------------|
| **Path** | None — must resolve via questioning; no silent path guess |
| **Artifact type** | Narrowest fit from Classify table; state once if inferred from context |
| **Action** | design-assist only if verb unclear after 1 AskQuestion |
| **Outcome preservation (fix)** | Existing artifact intent unchanged unless user signals redesign |
| **Audience** | Agent runtime if artifact is skill/command/agent/workflow; human if command-only UX |
| **Failure mode** | "Silent wrong behavior" if not specified for extract drafts only |

## Retry caps

| Class | Max rounds | Beyond cap |
|-------|------------|------------|
| Path resolution | 2 AskQuestion rounds | Stop: "Cannot proceed without a target path." |
| Action routing | 1 AskQuestion | Default to design-assist; state default |
| Contradiction resolution | 1 AskQuestion | Conservative default (fix < redesign < create) or stop if unresolvable |
| Unclear instruction | 1 AskQuestion + 1 open ask | Proceed with stated assumption |
| Write gate revision | 2 cycles | Draft-only in chat; "Manual review required." |

## Contradiction detection

Trigger when the same message contains conflicting signals:

| Pattern | Example | Route |
|---------|---------|-------|
| Fix + outcome change | "fix the wording but also change what it does" | **fix-vs-redesign** gate |
| Redesign + polish only | "redesign but only fix typos" | **fix-vs-redesign** gate |
| Conflicting verbs | "audit and rewrite" | AskQuestion: audit first or rewrite? |
| Type mismatch | "make this command a skill" | Classify → pick narrowest; flag type change as redesign |
| Scope conflict | Two unrelated outcomes in one request | Advisory critique → suggest split |

**Conservative default order** (when unresolved after 1 round): **fix** < **redesign** < **create** — prefer the least disruptive action and state the default.

**Hard stop:** If contradiction remains after 1 round and conservative default is unsafe → "Conflicting signals: [A] vs [B]. Rephrase and re-invoke." Stop.
