# Skill README spec (bidirectional)

Sibling `README.md` in a skill folder is the **human spec**—Why, What, When, and interaction contract—not a Procedure echo. The executor lives in `SKILL.md`. Both directions share the same contract.

| Direction | Input | Output | Action |
|-----------|--------|--------|--------|
| Spec → definition | README (or draft spec) | `SKILL.md` (+ refs as needed) | **create** / **design** |
| Definition → spec | `SKILL.md` (+ refs for constraints, not Procedure dump) | `README.md` | **extract** |

**Invariant:** Once a README ships, Why/What/When must not live only in `SKILL.md`. README must not paste **Procedure**. If the same paragraph appears in both, that is `SPEC_DEFINITION_DRIFT`—delete from README or link once.

## Scannable section model

**Goal is not a short README—it is a skimmable README.**

| Pattern | Readability |
|---------|-------------|
| Many **named sections**, each answering one question, **dense** content | Fast—reader jumps to Actions, When, UX |
| One **small file** with no headings, mixed concerns | Slow—cannot skip; must read everything |
| Long file, **verbose** prose, repeated ideas | Slow—even with headings |

**Rule:** Prefer **more sections with less per section** over fewer sections with more prose. Each `##` is a jump target. Subsections (`###`) group related bullets without new top-level noise.

**Density budget:** ~1 screen per section for orchestrator skills; entire README ≤2–3 screens if every section earns its heading.

Use `templates/readme.template.md`. Section read order:

| Section | Holds | Required |
|---------|--------|----------|
| H1 + one sentence | Skill id/title and one-line outcome | Yes |
| **Why** | Problem, audience, falsifiable done-when | Yes |
| **What** | Domain, types, boundaries; `### Verification` when non-obvious | Yes |
| **Actions** | id, outcome, pick-when table (orchestrator skills only) | Yes if ≥3 actions |
| **When** | `### Use when` + `### Avoid when` | Yes |
| **Philosophy** | 3–6 methodology invariants (eval-first, scoped-only, gates) | If eval-first, gates, or methodology |
| **UX** | `###` Invoke, Intake, Clarify, Output, Close | If clarify loops, gates, or multi-step close |
| **Design notes** | 2–4 non-obvious product tradeoffs | Optional—≥2 surprising tradeoffs |
| **Constraints** | Facts to regenerate `SKILL.md` (invoke, gates, paths) | Yes |
| **Notes** | Paths, install hints | Optional footer |

### Reader questions → sections

| Question | Section |
|----------|---------|
| Why exist? | **Why** |
| What domain? | **What** |
| What can I do? | **Actions** |
| When invoke / when avoid? | **When** → Use when / **Avoid when** |
| What principles never break? | **Philosophy** |
| How does it feel to use? | **UX** |
| Why these odd choices? | **Design notes** |
| What rebuilds SKILL.md? | **Constraints** |
| Where are files? | **Notes** |

## When → Use when / Avoid when

Anti-triggers are **required signal**. Keep them under **## When**, not a separate top-level heading.

| Layer | Anti-triggers |
|-------|---------------|
| **SKILL.md** | **When not to use** section (`skill.anti-triggers`) |
| **README.md** | **### Avoid when** under **## When** |

### Three concepts (dedupe rule)

| Concept | Home in README | Example |
|---------|----------------|---------|
| **Out-of-scope** | **What** (one short list) | "Does not implement application code" |
| **Anti-trigger / mis-invocation** | **When → Avoid when** | "Ambient repo review without a target path" |
| **Principle behind avoidance** | **Philosophy** (one line) | "Never ambient—always scoped path" |

**Dedup:** If the same bullet fits two homes, pick **Avoid when** for mis-invocation, **What** for capability boundary. Do not repeat across What + Avoid when + Philosophy.

**SKILL derivation at create/design:**

- **When to use** ← `### Use when` bullets (verbatim or tightened)
- **When not to use** ← `### Avoid when` bullets (+ What out-of-scope only if not already listed)
- `description` invoke-fit ← Use when + Avoid when condensed

## Actions (orchestrator skills)

Required table when sibling `SKILL.md` has an **Actions** table or ≥3 action ids:

| Action | Outcome | Pick when |
|--------|---------|-----------|

- **Pick when** = design routing (README only)
- **Run** ref column = SKILL only
- Not Procedure

## Philosophy

Short bullet list (3–6 items). Eval-first, scoped-only, spec/executor split, gates-before-write, etc.

**SKILL derivation:** Advisory tone, Purpose emphasis—not pasted into Procedure.

## UX

Structured with `###` sub-headings for jump targets:

```markdown
## UX

### Invoke
Slash or explicit Read; not ambient.

### Intake
Plain request → classified action.

### Clarify
Active AskQuestion on path, action, type, scope; one at a time; verbose by default.

### Output
Stage banners; PASS/FAIL evidence; draft-only on gate fail.

### Close
Next Up / AskQuestion; no slash deferral.
```

**SKILL derivation:** Execution rules, Exit conditions, questioning defaults.

## Design notes (optional)

Non-obvious **product** tradeoffs a reviewer must agree with—not process meta.

- `disable-model-invocation` because orchestrator is expensive
- Dual close surface (skill AskQuestion vs command homework)
- Write blocked on STATIC SKIPPED unless draft-only

**Not:** "we run static audit" (that's What/Constraints). **Not:** Procedure steps.

**Include when:** ≥2 tradeoffs that would surprise a new author. **Omit** when Philosophy already covers them.

## What → Verification

Keep verification under **What** as `### Verification`—not a top-level `##`:

```markdown
## What
…domain and types…

### Verification
Mechanical static audit; judgment type rubrics; prompt-based behavior probes.
```

Avoid paths here—concept names only. Paths belong in **Notes**.

## Reconstructability (SKILL ← README)

| SKILL section | README source |
|---------------|---------------|
| `description` | Constraints draft + Use when / Avoid when condensed |
| Purpose | Why |
| When to use | When → Use when |
| When not to use | When → Avoid when (+ What out-of-scope if unique) |
| Actions table | Actions (id, outcome) |
| Procedure | Constraints phases + UX habits (names only) |
| Exit conditions | Constraints stops + UX clarify caps |
| Execution rules | UX subsections |

## What README does not hold

| Does not hold | Belongs in |
|---------------|------------|
| Step-by-step **Procedure** | `SKILL.md` |
| Orchestration gate scripts | `refs/gate-prompts.md`, action refs |
| Full rubric tables | `refs/rubrics/` |
| File-tree dumps without problem statement | Nowhere—rewrite as **What** or **Notes** |
| Process meta ("we research first") | Advisory only—not product spec |

## Two-way rules

**Extract (SKILL → README):** Ingest `SKILL.md` + progressive-disclosure refs for **constraints** (invoke, gates, eval-first, paths). Do **not** copy **Procedure** steps or Load chains. Map **When not to use** → `### Avoid when`; **When to use** → `### Use when`. Fill Actions table + pick-when from classify routing. Derive Philosophy / UX / Design notes from advisory, questioning, close-contract, frontmatter tradeoffs. Paths → **Notes** only. Fill `readme.template.md`. Record provenance: source paths + assumptions.

**Create / design (README → SKILL):** If README is missing, draft spec first (or record defer reason). If README exists and user asked for `SKILL.md`, do not invent a second spec—derive executor from README + type template. Draft order: README spec → `SKILL.md` → refs only when template or FAIL requires.

**Validate:** (1) Human one-pass—junior reader understands Why/What/When without opening `SKILL.md`. (2) Reverse direction still works—README alone could regenerate a coherent `SKILL.md` outline.

## Clarity rules (inlined)

Apply on every README draft. No runtime load of external humanize plugins.

### Structure

| Pattern | Detect | Fix |
|---------|--------|-----|
| Parallel negation | "Not only… but also…", stacked "It's not X, it's Y" | State the positive claim once |
| Tricolon / rule of three | Three parallel phrases where one suffices | Cut to one or two; keep if list is factual |
| Rhetorical Q+A | Question answered in the next sentence | Merge or drop the question |
| Mirror sentences | Same opener 3+ times in a row | Vary length and lead |
| Significance inflation | "pivotal", "landscape", "testament", "underscores the importance" | Plain verb or drop |
| Copula avoidance | "serves as", "stands as", "boasts", "features" for simple `is`/`has` | Prefer `is`/`has` when meaning unchanged |

### Flow

- **Given–new:** start with known info; end with the new point.
- **One idea per sentence** — split stacked clauses.
- **SVO close:** subject–verb–object near the start when possible.
- **Chunking:** short lead sentence, then detail.
- **Repeat key nouns** — avoid elegant variation that hides the referent.

### Punctuation and rhythm

- Prefer period or comma over em dash, semicolon glue, or mid-clause colon.
- Mix short and long sentences; avoid uniform ~18-word runs.

## Anti-patterns (audit when cheap)

| Anti-pattern | Label |
|--------------|-------|
| README restates SKILL **Procedure** or Load chains | `SPEC_DEFINITION_DRIFT` |
| Goals/Scope/Audience/When-to-use copied from SKILL headings | Template echo—not a spec |
| File tree without stating what problem the skill solves | `SPEC_VAGUE` |
| "Non-obvious choices" that only describe CE process | Process meta—not product tradeoff |
| README longer than SKILL without unique spec content | NOISE risk |
| Why/What/When missing or empty | `readme-spec` FAIL |
| Anti-triggers duplicated across What and Avoid when | Dedup violation |
| Paths above **Notes** | `readme-spec` FAIL (judgment) |

## Create/fix minimum

When **create** or **design** ships a skill folder:

1. `SKILL.md` + `README.md` both exist **or** user explicitly defers README with reason in chat.
2. README answers in ≤1 screen per section: **Why**, **What**, **When** (with Use/Avoid subsections)—without duplicating Procedure.
3. Orchestrator README includes **Actions** table when SKILL has ≥3 actions.
4. Optional: link to test probes or audit rubric—do not paste rubric tables wholesale.

When user defers README: list as open question; do not block extract chat-only drafts.
