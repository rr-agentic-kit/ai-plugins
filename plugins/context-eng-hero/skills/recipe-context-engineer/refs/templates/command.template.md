---
name: your-command-id
description: User-facing outcome in one sentence ≤160.
# argument-hint: "[path] [--flag]"   # Claude: when slash expects args
# allowed-tools: Read, Grep          # Claude: side-effect narrowing only when needed
# model: sonnet                      # Claude: omit unless product requires pin
---

# <!-- REQUIRED: command heading -->

## Input contract

<!-- REQUIRED: what user/agent must supply -->

## Execution

Execute **Action: …** in skill **<!-- REQUIRED: skill id -->**.

<!-- Do NOT route solely by telling the user to chain other slashes. Use Load + steps in the skill Action, or delegate to a skill Action. -->

## Output

<!-- REQUIRED (command.output.shape): shape of response -->
