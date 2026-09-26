---
name: rr-coder
description: Production code standards (SOLID, CPNNN, architecture). Via --coder, review code lane, or orchestrate plan/build (drive/scope per parent).
disable-model-invocation: true
---

# rr-coder

**Human overview:** [README.md](README.md)

## Purpose

Apply production code standards (SOLID, CPNNN rubric, architecture, observability, language refs) to **application source** only. Tests and test strategy live under **rr-tester**; rr-tester loads this skill so test **code** matches implementation rules.

## When to use

- Implement or refactor production/application source via **rr-builder** `--coder` (full-skill handoff) or **rr-review** code lane
- Also loaded under **rr-builder** orchestration: **plan** stage = knowledge refs only (no source edits); **build** stage = full skill for the step
- Code lane review with CP finding table and mandatory **`## Architecture`** section

## When not to use

| Need | Use instead |
|------|-------------|
| Test gaps, MISSING verdicts | **rr-tester** |
| OWASP / exploitability | **rr-security-auditor** |
| MR inline POST | **rr-ci** after **rr-review** `--ci` |

## Procedure

Single-shot implement with known stack: TodoWrite N/A. Delivery channels: N/A — no AskQuestion gates here (parent **rr-builder** owns confirms). Task agents: N/A — path-loaded `Read` only.

1. **load** — Read refs from **Required Knowledge** in order; load language ref when stack is identified. Done: principles loaded before edits or findings.
2. **apply** — For implement/refactor: apply loaded principles and language refs; load [testability.md](refs/testability.md) when tests will follow. When co-editing tests or when **rr-tester** loads this skill, apply language Prefer/Avoid for assertions at write time (e.g. TypeScript S5906 most-specific matchers)—do not defer assertion style to post-hoc Sonar. For TypeScript `process`/`Buffer` name errors, run the **Node types probe** in [typescript.md](refs/typescript.md) before installing packages or rewriting imports. For review: full LOAD list; exclude dedicated test paths from production findings. Done: principles applied to scoped source, or review scope enumerated with dedicated test paths excluded.
3. **emit** — When reviewing: map findings via [compliance-rubric.md](refs/compliance-rubric.md); triage via [severity-triage.md](refs/severity-triage.md); emit CP table then mandatory **`## Architecture`**. When brief path is set, **Read** it once — do not re-fetch linked tickets. Done: findings or applied changes match loaded refs.

Fix path: inline apply in the parent session. When **rr-review** `--fix` routes code findings, follow the review plan steps.

## Required Knowledge

Load via explicit `Read`, in order. Matrix below is intentional — stack detection requires a lookup table, not prose.

1. **Universal (always)** — [code.principles.md](refs/code.principles.md). If no language ref matches, apply principles only.
2. **Review / classification (when reviewing)** — [compliance-rubric.md](refs/compliance-rubric.md). For SRP/cohesion (**CP022** / **CP015**), also [srp-cohesion.md](refs/srp-cohesion.md). For test seams (**CP015** / **CP004** / **CP024** / **CP022**), [testability.md](refs/testability.md). For architecture (**AR001**–**AR004**), [architecture.md](refs/architecture.md).
3. **Emit / Challenge gate (when reviewing)** — [severity-triage.md](refs/severity-triage.md) after the rubric.
4. **Observability (review or refactor)** — [observability.md](refs/observability.md) (**CP027**–**CP029**). Not required for net-new implement-only paths.
5. **Language / framework (additive)** — When stack is identified:

| Stack | Ref |
|-------|-----|
| Java (`.java`) | [java.md](refs/java.md) + version: [java-17](refs/java-17.md) / [java-21](refs/java-21.md) / [java-25](refs/java-25.md) |
| Java + Spring | [java.spring.md](refs/java.spring.md), [orm-principles.md](refs/orm-principles.md) |
| Kotlin | [kotlin.md](refs/kotlin.md) |
| TypeScript | [typescript.md](refs/typescript.md) |
| React | [react-18.md](refs/react-18.md) |
| React + REST | [react-query.md](refs/react-query.md) |
| React + GraphQL | [react-apollo.md](refs/react-apollo.md) |
| Tauri v2 | [tauri-v2.md](refs/tauri-v2.md) |
| Vue 3 | [vue-3.md](refs/vue-3.md) |
| Python | [python.md](refs/python.md) |
| Rust | [rust.md](refs/rust.md) |
| Go 1.26+ | [go-1.26.md](refs/go-1.26.md) |
| LLM integration | [ai-engineer.md](refs/ai-engineer.md), [langchain.md](refs/langchain.md), [langgraph.md](refs/langgraph.md) |
