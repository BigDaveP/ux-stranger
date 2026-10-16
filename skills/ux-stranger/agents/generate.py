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
# Replace with the cheapest vision-capable model ID from Cursor's models page; `inherit` also works.
model: inherit
readonly: true
---
{note}{prompt}
"""
assert "'''" not in prompt
codex = f'''# Generated from references/tester-prompt.md — edit that file and regenerate.
name = "ux-tester"
description = "{desc}"
# Use the cheapest vision-capable model on your plan (check `codex` model list).
model = "gpt-5.4-mini"
# No file writes; the tester only needs the browser MCP.
sandbox_mode = "read-only"
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
