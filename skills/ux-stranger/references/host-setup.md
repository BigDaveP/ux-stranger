# Host setup

The skill itself (`SKILL.md` + `references/` + `templates/`) is the same everywhere. Only two things change per host: **where the skill folder goes** and **how the `ux-tester` sub-agent is declared**. No API key is needed. Each host runs the tester with the user's existing subscription/session.

**Quickest for Claude Code:** install the plugin from GitHub. It brings the skill and the `ux-tester` sub-agent in one step, so you can skip sections 1 and 2:

```bash
claude plugin marketplace add BigDaveP/ux-stranger
claude plugin install ux-stranger@ux-stranger
```

The plugin also bundles Playwright MCP (`.mcp.json` at the plugin root: `npx @playwright/mcp@0.0.85 --isolated --output-dir ux-stranger/.playwright-mcp`, pinned so behaviour doesn't drift), so the browser is set up too, including in cloud sessions. If you had added your own `playwright` server before, remove it (`claude mcp remove playwright`): otherwise the tester sees two browsers' tools.

## 1. Install the skill folder

| Host | Project-level | User-level |
|---|---|---|
| Claude Code | `.claude/skills/ux-stranger/` | `~/.claude/skills/ux-stranger/` |
| Codex | `.agents/skills/ux-stranger/` | `~/.agents/skills/ux-stranger/` (or `~/.codex/skills/`) |
| Cursor | `.agents/skills/ux-stranger/` or `.cursor/skills/ux-stranger/` | `~/.agents/skills/` or `~/.cursor/skills/` |

Tip: put it in **`.agents/skills/ux-stranger/`** in the repo. Codex and Cursor read it there natively. For Claude Code, add a symlink: `ln -s ../../.agents/skills/ux-stranger .claude/skills/ux-stranger`. Cursor also reads `.claude/skills/`.

## 2. Install the `ux-tester` sub-agent

| Host | Copy | To |
|---|---|---|
| Claude Code | `agents/claude/ux-tester.md` | `.claude/agents/ux-tester.md` |
| Cursor | `agents/cursor/ux-tester.md` | `.cursor/agents/ux-tester.md` |
| Codex | `agents/codex/ux-tester.toml` | `.codex/agents/ux-tester.toml` |

Cursor also reads `.claude/agents/`, but its `model` values differ. Keep the Cursor-specific file in `.cursor/agents/`; it takes precedence when names collide.

### Picking the tester model

Use the **cheapest capable model with vision** your plan offers. The model IDs in the agent files are defaults. Check them against your host's current model list:
- Claude Code: `haiku` (alias).
- Codex: `gpt-6-luna` (the faster, lower-cost model in the Codex docs).
- Cursor: `inherit` by default (your current model). Set a faster model ID from Cursor's models page for a cheaper tester; the isolation rules make the test meaningful either way.

If the tester model fails on *trivial* steps (can't click a clearly labelled button), it is too weak to be informative. Step up one tier.

## 3. Give the tester a browser

Playwright MCP works in all three hosts.

**Claude Code**

Nothing to do with the plugin install: Playwright MCP is bundled. Without the plugin (skill copied by hand):
```bash
claude mcp add playwright -- npx @playwright/mcp@0.0.85 --isolated
```

**Cloud and remote sessions** (Claude Code on the web, the mobile app, GitHub Actions)

The container starts fresh each session, so anything you added with `claude mcp add` on your own machine is not there. Chromium is preinstalled and `npx @playwright/mcp@0.0.85` runs as is; the server only needs to be *declared*:
- Plugin enabled in the session → nothing to do, the bundled server starts. Note: a skill uploaded on its own (claude.ai skills) can't declare an MCP server; install the plugin instead.
- Session already started without it → section 5 (headless tester fallback), no restart needed.
- Skill only (no plugin) → add this line to the environment's **setup script** (cloud environment settings), which runs before each session:
  ```bash
  claude mcp add --scope user playwright -- npx -y @playwright/mcp@0.0.85 --isolated
  ```
  Or commit a `.mcp.json` declaring the same `playwright` server at the root of the project under test.
- The network policy must allow the npm registry (it does by default) for `npx` to download the server.

**Codex**: `~/.codex/config.toml`
```toml
[mcp_servers.playwright]
command = "npx"
args = ["@playwright/mcp@0.0.85"]
```
Codex sub-agents inherit the parent session's MCP servers, sandbox and approval settings (they can't be set in the agent file). The tester file turns off the shell tool so it can only use the browser. If the browser can't start or reach `localhost`, allow network access for the session or test against a deployed preview URL.

Invoke the skill with `$ux-stranger` (or from `/skills`).

**Cursor**: `.cursor/mcp.json`
```json
{ "mcpServers": { "playwright": { "command": "npx", "args": ["@playwright/mcp@0.0.85"] } } }
```
Local Cursor sub-agents inherit the parent's MCP servers. The tester is `readonly: true`; if its browser actions get blocked, set `readonly: false` in `.cursor/agents/ux-tester.md`. Cursor's built-in browser also works if your version exposes it to sub-agents. Invoke the skill with `/ux-stranger`.

Recommended: a fresh, isolated browser profile per run (Playwright MCP `--isolated`), so a previous run's state doesn't leak into the next, and `--output-dir ux-stranger/.playwright-mcp` so screenshots and page snapshots stay in the (git-ignored) `ux-stranger/` folder. Pin the version (`@playwright/mcp@x.y.z`): page-snapshot behaviour changes between releases.

## 4. Fallback: no custom sub-agent support

Spawn any generic sub-agent (or a second session). Paste the full content of `references/tester-prompt.md` followed by the task brief. Tell it explicitly that it has no access to the repository. Results are slightly less reliable because model and tools aren't pinned, but the method still holds.
## 5. Fallback: no browser tool in this session (Claude Code)

MCP servers load when a session starts, so a session that began without Playwright MCP (skill uploaded on its own instead of the plugin, project `.mcp.json` added mid-session, server disconnected) can't get it back. Don't ask for a new session and don't build a substitute browser: run each tester as a **separate headless Claude Code session** that declares its own browser and may use **only** the browser tools. Isolation is stricter than with a sub-agent: the tester can't read files or run commands.

From the project root, once per run (runs can be parallel in comprehension mode, or when tasks don't mutate shared data):

```bash
SKILL_DIR=<path to the ux-stranger skill folder>
MCP='{"mcpServers":{"playwright":{"command":"npx","args":["-y","@playwright/mcp@0.0.85","--isolated","--output-dir","ux-stranger/.playwright-mcp"]}}}'
TOOLS=$(printf 'mcp__playwright__%s,' browser_navigate browser_navigate_back browser_snapshot browser_take_screenshot browser_click browser_type browser_fill_form browser_select_option browser_hover browser_press_key browser_wait_for browser_handle_dialog browser_tabs browser_resize | sed 's/,$//')
mkdir -p ux-stranger/reports/runs
claude -p --model haiku --strict-mcp-config --mcp-config "$MCP" \
  --allowedTools "$TOOLS" \
  --disallowedTools "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,Agent,Task,NotebookEdit,Skill" \
  --append-system-prompt "$(cat "$SKILL_DIR/references/tester-prompt.md")" \
  "$BRIEF" < /dev/null > "ux-stranger/reports/runs/<run-id>.json"
```

- `$BRIEF` is the usual brief (task or comprehension), as plain text.
- The report is the last JSON object in the output file. Extract it and validate it against the schema, exactly as with a sub-agent's report.
- Never add `--permission-mode bypassPermissions` or `--dangerously-skip-permissions`: the allow-list above is all the tester needs, and auto mode refuses those flags.
- `--strict-mcp-config` keeps the user's other MCP servers away from the tester.
- For the panel mode's other vendors, keep using their own CLIs (`modes.md`).
