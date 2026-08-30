# Install ai-plugins

Install the **ai-plugins** marketplace ([rr-agentic-kit/ai-plugins](https://github.com/rr-agentic-kit/ai-plugins)) into **Claude Code** or **Cursor**. Plugins: `context-eng-hero`, `rrraw`, `jobseeker`.

## Install via AI (recommended)

Paste this into Claude Code or Cursor Agent:

```text
Read and follow the instructions in https://raw.githubusercontent.com/rr-agentic-kit/ai-plugins/master/INSTALL-AI.md to install or update ai-plugins (context-eng-hero, rrraw, jobseeker) into my current AI runtime. Detect whether I'm in Claude Code or Cursor. Ask me which plugins to apply, label each as "install" or "update", then run only what I select.
```

The agent follows [INSTALL-AI.md](INSTALL-AI.md) (runtime detection, plugin selection with install/update labels, verify, troubleshooting).

## Manual install — Claude Code

1. Add the marketplace:

   ```text
   /plugin marketplace add rr-agentic-kit/ai-plugins
   ```

   Alternatives: full Git URL, or a local path to this repo root for monorepo dev.

2. Install each plugin:

   ```text
   /plugin install context-eng-hero@ai-plugins
   /plugin install rrraw@ai-plugins
   /plugin install jobseeker@ai-plugins
   ```

3. Non-interactive equivalent:

   ```bash
   claude plugin marketplace add rr-agentic-kit/ai-plugins
   claude plugin install context-eng-hero@ai-plugins --scope user --yes
   claude plugin install rrraw@ai-plugins --scope user --yes
   claude plugin install jobseeker@ai-plugins --scope user --yes
   ```

4. If the install summary asks for it, run `/reload-plugins`.

5. Verify: `claude plugin list` (or `/plugin` TUI).

**Monorepo / local checkout:** from the repo root, `uv run python scripts/install_claude_local.py` adds or repoints the local marketplace and installs/updates each catalog plugin.

## Manual install — Cursor

### Individual (recommended)

No Teams/Enterprise plan required. Cursor discovers plugins under `~/.cursor/plugins/local/` when **Allow Local Plugin Imports** is not disabled (Enterprise-only default-off setting).

1. Fetch plugins into a **temporary** clone, **copy** each plugin directory into the local plugins folder (do not leave a permanent checkout), then remove the temp clone:

   ```bash
   TMP="$(mktemp -d)"
   git clone --depth 1 https://github.com/rr-agentic-kit/ai-plugins.git "$TMP/ai-plugins"
   mkdir -p ~/.cursor/plugins/local
   for name in context-eng-hero rrraw jobseeker; do
     rm -rf ~/.cursor/plugins/local/"$name"
     cp -R "$TMP/ai-plugins/plugins/$name" ~/.cursor/plugins/local/"$name"
   done
   rm -rf "$TMP"
   ```

2. In Cursor: **Developer: Reload Window** (or restart Cursor).

3. Verify: open **Customize** in the sidebar and confirm `context-eng-hero`, `rrraw`, and `jobseeker` appear with their skills/commands.

If you already have this repo checked out for development, you may instead symlink `plugins/<name>` into `~/.cursor/plugins/local/<name>` and skip the temp clone—keep the checkout if you do that.

### Team / Enterprise

Dashboard → **Plugins** → **Team Marketplaces** → **Add Marketplace** → paste the repo URL. Requires a Teams/Enterprise plan.

## Updating

| Runtime | Steps |
|---------|--------|
| Claude Code | `/plugin update context-eng-hero@ai-plugins` (repeat per plugin), or re-run the non-interactive install commands / `scripts/install_claude_local.py` for a local marketplace. |
| Cursor (local copy) | Re-run the temp-clone + `cp -R` block above, then **Developer: Reload Window**. |
| Cursor (dev symlink) | `git pull` in the checkout, then reload the window. |

## Uninstalling

| Runtime | Steps |
|---------|--------|
| Claude Code | `claude plugin uninstall <name>@ai-plugins` (e.g. `context-eng-hero@ai-plugins`). |
| Cursor | Remove `~/.cursor/plugins/local/<name>` (or the symlink), then reload the window. |

## Troubleshooting

If something fails, paste the error into your AI chat along with [INSTALL-AI.md](INSTALL-AI.md)—it has a troubleshooting table.

## See also

- [README.md](README.md) — plugin usage and repo overview
- [CONTRIBUTING.md](CONTRIBUTING.md) — monorepo development, tests, CI
