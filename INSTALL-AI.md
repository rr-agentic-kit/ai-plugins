# INSTALL-AI.md — agent install runbook

Execute these steps. Prefer shell commands over prose. Ask the user only for: (1) which plugins to install/update (required — Step 1), (2) reload Cursor when needed, (3) blockers (missing auth, missing CLI).

## Goal

Install or update selected **ai-plugins** marketplace plugins into the user’s current AI runtime.

| Fact | Value |
|------|--------|
| Marketplace name | `ai-plugins` |
| Repo | `https://github.com/rr-agentic-kit/ai-plugins` |
| GitHub shorthand | `rr-agentic-kit/ai-plugins` |
| Catalog plugins | `context-eng-hero`, `rrraw`, `jobseeker` |
| Scope (Claude CLI) | `user` |

Happy path needs no external doc lookups. If a command fails in a way not covered below, fetch the drift URLs in **Where to re-check for drift**.

## Step 0 — detect runtime

Branch on the session:

1. **Claude Code** if any of: `claude` is on `PATH`, the user is in a Claude Code session, or slash commands like `/plugin` are available.
2. **Cursor** if any of: Cursor Agent / IDE context, `~/.cursor` exists as the product home, or the user is clearly in Cursor.
3. If both signals appear, prefer the product the user is actively using for this chat. If still ambiguous, run Claude steps when `claude` works; otherwise Cursor steps.
4. Proceed to **Step 1** (plugin selection), then **Step A** (Claude) or **Step B** (Cursor).

## Step 1 — ask which plugins; label install vs update

**Required.** Do not install or update anything until the user chooses.

1. Detect which catalog plugins are **already present**:
   - **Claude Code:** `claude plugin list` — treat as present if `name@ai-plugins` (or equivalent) is listed.
   - **Cursor:** present if `~/.cursor/plugins/local/<name>` exists (directory or symlink).
2. Build a plan line per catalog plugin using exactly this format (one line each):

   ```text
   context-eng-hero install
   rrraw update
   jobseeker install
   ```

   Rules:
   - `{plugin name} install` — not present yet.
   - `{plugin name} update` — already present.
3. Show that list to the user and ask which plugins to apply (any subset, or all). Wait for the answer.
4. Operate **only** on the plugins the user selected. For each selected name, use `install` or `update` as labeled above (do not re-label after the user answers unless presence changed).

After selection, go to Step A or Step B.

## Step A — Claude Code

Run in order for the **selected** plugins only. Use the CLI when available; slash commands are equivalent in an interactive Claude Code session.

### A1. Add marketplace

```bash
claude plugin marketplace add rr-agentic-kit/ai-plugins
```

Expected: marketplace `ai-plugins` listed afterward.

```bash
claude plugin marketplace list
```

**Name collision / wrong source:** if `ai-plugins` already exists and points elsewhere (or add fails because the name is taken), remove and re-add:

```bash
claude plugin marketplace remove ai-plugins --scope user
claude plugin marketplace add rr-agentic-kit/ai-plugins
```

For a **local monorepo checkout** (dev), add the repo root path instead of the GitHub shorthand, or run `uv run python scripts/install_claude_local.py` from the repo root (idempotent add/repoint + install/update of the full catalog—only use that script if the user wants every catalog plugin).

### A2. Install or update selected plugins

For each selected plugin, run the action from Step 1:

**install:**

```bash
claude plugin install <name>@ai-plugins --scope user --yes
```

**update:**

```bash
claude plugin update <name>@ai-plugins --scope user
```

Slash equivalents: `/plugin install <name>@ai-plugins` or `/plugin update <name>@ai-plugins`.

Expected: each command succeeds, or update reports already at latest version (not a failure—see troubleshooting).

After applying, report the outcome using the same line format, e.g.:

```text
context-eng-hero install
rrraw update
```

### A3. Reload if required

If the install/update summary says plugins need a reload, run `/reload-plugins` (or tell the user to run it). Restart Claude Code if hooks/MCP changes did not load after reload.

### A4. Verify

```bash
claude plugin list
```

Confirm each **selected** `*@ai-plugins` plugin appears. Then jump to **Verification checklist**.

## Step B — Cursor

Do **not** rely on Team Marketplace import unless the user is on Teams/Enterprise and asks for it. Default path: copy **selected** plugin trees into `~/.cursor/plugins/local/` from a **temporary** clone, then delete the clone. Do not leave a permanent checkout unless the user already has one for development.

Both `install` and `update` for Cursor mean: replace `~/.cursor/plugins/local/<name>` with a fresh copy (or symlink in the dev path below). Keep the Step 1 labels when reporting.

### B1. Ensure local plugins directory

```bash
mkdir -p ~/.cursor/plugins/local
```

### B2. Temp clone → copy selected → remove clone

Replace `SELECTED` with the space-separated names the user chose:

```bash
TMP="$(mktemp -d)"
git clone --depth 1 https://github.com/rr-agentic-kit/ai-plugins.git "$TMP/ai-plugins"
for name in SELECTED; do
  rm -rf ~/.cursor/plugins/local/"$name"
  cp -R "$TMP/ai-plugins/plugins/$name" ~/.cursor/plugins/local/"$name"
done
rm -rf "$TMP"
```

Report applied actions in the same format:

```text
context-eng-hero install
rrraw update
```

**Already in a monorepo checkout (dev only):** you may symlink **selected** plugins instead and keep the checkout:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
mkdir -p ~/.cursor/plugins/local
for name in SELECTED; do
  ln -sfn "$REPO_ROOT/plugins/$name" ~/.cursor/plugins/local/"$name"
done
```

### B3. User must reload (agent cannot)

Instruct the user to run **Developer: Reload Window** (or restart Cursor). Do not edit Cursor settings JSON to force this.

### B4. Verify (user-assisted)

Ask the user to open **Customize** in the sidebar and confirm the **selected** plugins show skills/commands. Optionally list dirs:

```bash
ls -la ~/.cursor/plugins/local
```

## Verification checklist

### Claude Code

- [ ] `claude plugin marketplace list` includes `ai-plugins` with the intended source.
- [ ] `claude plugin list` includes each **selected** `*@ai-plugins` plugin.
- [ ] A selected plugin’s command is callable (after reload if required).

### Cursor

- [ ] Each **selected** name exists under `~/.cursor/plugins/local/` (dir or valid symlink).
- [ ] User reloaded the window.
- [ ] Customize shows the selected plugins.

## Troubleshooting

| Condition | Cause | Fix |
|-----------|--------|-----|
| Claude: marketplace name already points elsewhere | Stale/other `ai-plugins` registration | `claude plugin marketplace remove ai-plugins --scope user` then re-add the correct source |
| Claude: install says “already at latest version” | Version pinned in `plugin.json`; nothing newer to fetch | Not an install error; needs an upstream version bump to get new code via marketplace update |
| Claude: git auth failures over SSH | Host key / agent / SSH-only remote | Ensure host in `known_hosts` and key in `ssh-agent`, or set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` and retry with HTTPS |
| Claude: installed but skills/commands missing | Runtime not reloaded | `/reload-plugins`; restart for hooks/MCP |
| Cursor: plugin missing after copy/symlink | Local imports disabled (Enterprise) or no reload | Confirm **Allow Local Plugin Imports** is not disabled; reload window again |
| Cursor: marketplace copy shadows local | Marketplace install wins over local folder | Uninstall the marketplace version of that plugin first, keep local under `~/.cursor/plugins/local/` |
| Cursor: no Teams/Enterprise plan | Dashboard marketplace import unavailable | Use Step B (local folder copy); do not use Team Marketplaces |
| Temp clone fails (network/git) | Clone URL or connectivity | Retry HTTPS clone; if blocked, ask user for network/auth help—do not invent alternate remotes |

## Where to re-check for drift

If a command errors in a way not covered above, fetch these live and adapt (do not guess outdated flags):

- https://code.claude.com/docs/en/plugin-marketplaces
- https://code.claude.com/docs/en/plugins-reference.md
- https://cursor.com/docs/plugins.md
- https://cursor.com/docs/reference/plugins

Human-facing summary: [INSTALL.md](INSTALL.md) in this repo (or the same path on `master`).

## Never do

- Do not force-push to any remote.
- Do not edit global Cursor or Claude settings files directly to “fix” install.
- Do not fabricate a plugin version bump to work around a cache or “already at latest” message.
- Do not leave a temporary clone behind after a successful Cursor copy install.
- Do not install or update any catalog plugin the user did not select in Step 1.
- Do not skip Step 1 or invent a default selection (including “all three”) without the user’s answer.
