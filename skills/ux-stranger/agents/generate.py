import pathlib
root = pathlib.Path(__file__).resolve().parents[1]
prompt = (root/"references/tester-prompt.md").read_text().strip()
desc = "Naive usability-test participant. Completes a user goal in a browser by sight only, thinking aloud, and returns a JSON run report. Used by the ux-stranger skill; never give it code or repo context."
note = "<!-- Generated from references/tester-prompt.md — edit that file and regenerate, do not edit here. -->\n\n"

tools = ",".join("mcp__playwright__"+t for t in [
 "browser_navigate","browser_navigate_back","browser_snapshot","browser_take_screenshot",
 "browser_click","browser_type","browser_fill_form","browser_select_option","browser_hover",
 "browser_press_key","browser_wait_for","browser_handle_dialog","browser_tabs","browser_resize"])
claude = f"""---
name: ux-tester
description: {desc}
tools: {tools}
model: haiku
---
{note}{prompt}
"""
cursor = f"""---
name: ux-tester
description: {desc}
# `inherit` uses the parent's model. For a cheaper tester, set a fast model ID from Cursor's models page.\n# If browser (MCP) actions get blocked, set readonly: false; the tester prompt still forbids file changes.
model: inherit
readonly: true
---
{note}{prompt}
"""
assert "'''" not in prompt
codex = f'''# Generated from references/tester-prompt.md — edit that file and regenerate.
name = "ux-tester"
description = "{desc}"
# Faster, lower-cost model for the naive tester. Check your plan's model list.
model = "gpt-6-luna"
# The tester only needs the browser MCP (inherited from the parent session).
# Sandbox and MCP servers can't be set per agent in Codex; they come from the parent.
features.shell_tool = false
skills.include_instructions = false
developer_instructions = \'\'\'
{prompt}
\'\'\'
'''
for p, c in [("agents/claude/ux-tester.md", claude), ("agents/cursor/ux-tester.md", cursor), ("agents/codex/ux-tester.toml", codex)]:
    f = root/p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(c)
print("ok")

# When this skill lives inside the ux-stranger repo (Claude Code plugin layout),
# also refresh the plugin-level copy of the Claude agent.
repo = root.parents[1]
if (repo / ".claude-plugin").is_dir():
    (repo / "agents").mkdir(exist_ok=True)
    (repo / "agents" / "ux-tester.md").write_text((root / "agents/claude/ux-tester.md").read_text())
    print("plugin agent refreshed")