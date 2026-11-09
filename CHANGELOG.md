# Changelog

## 0.1.1 — 2026-11-09

- Claude Code plugin now bundles Playwright MCP (`.mcp.json`), so the tester has a browser in cloud sessions too
- Tester accepts both tool prefixes (`mcp__playwright__*` and `mcp__plugin_ux-stranger_playwright__*`)
- Skill: stop and explain when no browser tool is available, instead of building a substitute
- Docs: cloud / remote session setup

## 0.1.0 — 2026-10-16 (experimental)

First public version.

- Naive tester sub-agent for Claude Code, Cursor and Codex, generated from a single prompt
- Step-by-step workflow: app map → pick module/flow → approve tasks → run → in-chat report → fix / next / stop
- Modes: `lite-check`, standard, `panel` (multi-model consensus with a usage estimate)
- Flag rules, JSON run-report schema, task-writing guide, templates
- Claude Code plugin + marketplace manifests
- Safety: credentials from env var, prompt-injection guard in the tester, test-environment guidance
