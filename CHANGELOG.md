# Changelog

## 0.2.1 — 2026-11-10

- Fallback when a session has no browser tool: each tester runs as a headless Claude Code session with its own pinned Playwright MCP and only browser tools (no new session needed)
- Docs: a skill uploaded alone to claude.ai can't bring the browser; install the plugin

## 0.2.0 — 2026-11-09

- New `comprehension` mode for landing pages and public sites: client-defined personas, first impression + free exploration, comprehension table (first glance / late / misread / missed), fit and visual-tone check, copy fixes that never invent facts. Offered automatically when the map finds public pages
- `ux-stranger/positioning.yaml` stores the approved personas and intended message (template included)
- New flags: `MESSAGE_MISREAD`, `MESSAGE_MISSED`, `MESSAGE_LATE`, `FIT_REJECTED`, `FIT_HESITANT`, `TONE_MISMATCH`, `JARGON`; verdict `CLEAR` / `NEEDS WORK`
- Map modules get `kind: public | app`
- `scripts/check.py` consistency check for contributors
- Comprehension framing asks one question (which customers to attract) and one approval; the builder generates triggers, arrivals, leave reasons, viewports and the outsider choice
- Bundled Playwright MCP pinned to 0.0.85, writes screenshots and snapshots to `ux-stranger/.playwright-mcp/`

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
