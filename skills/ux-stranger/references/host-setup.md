# Host setup

The skill itself (`SKILL.md` + `references/` + `templates/`) is the same everywhere. Only two things change per host: **where the skill folder goes** and **how the `ux-tester` sub-agent is declared**. No API key is needed. Each host runs the tester with the user's existing subscription/session.

**Quickest for Claude Code:** install the plugin from GitHub. It brings the skill and the `ux-tester` sub-agent in one step, so you can skip sections 1 and 2:

```bash
claude plugin marketplace add BigDaveP/ux-stranger
claude plugin install ux-stranger@ux-stranger
```

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
```bash
claude mcp add playwright -- npx @playwright/mcp@latest
```

**Codex**: `~/.codex/config.toml`
```toml
[mcp_servers.playwright]
command = "npx"
args = ["@playwright/mcp@latest"]
```
Codex sub-agents inherit the parent session's MCP servers, sandbox and approval settings (they can't be set in the agent file). The tester file turns off the shell tool so it can only use the browser. If the browser can't start or reach `localhost`, allow network access for the session or test against a deployed preview URL.

Invoke the skill with `$ux-stranger` (or from `/skills`).

**Cursor**: `.cursor/mcp.json`
```json
{ "mcpServers": { "playwright": { "command": "npx", "args": ["@playwright/mcp@latest"] } } }
```
Local Cursor sub-agents inherit the parent's MCP servers. The tester is `readonly: true`; if its browser actions get blocked, set `readonly: false` in `.cursor/agents/ux-tester.md`. Cursor's built-in browser also works if your version exposes it to sub-agents. Invoke the skill with `/ux-stranger`.

Recommended: a fresh, isolated browser profile per run (Playwright MCP `--isolated`), so a previous run's state doesn't leak into the next.

## 4. Fallback: no custom sub-agent support

Spawn any generic sub-agent (or a second session). Paste the full content of `references/tester-prompt.md` followed by the task brief. Tell it explicitly that it has no access to the repository. Results are slightly less reliable because model and tools aren't pinned, but the method still holds.