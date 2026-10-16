# Changelog

## 0.1.0 — 2026-10-16 (experimental)

First public version.

- Naive tester sub-agent for Claude Code, Cursor and Codex, generated from a single prompt
- Step-by-step workflow: app map → pick module/flow → approve tasks → run → in-chat report → fix / next / stop
- Modes: `lite-check`, standard, `panel` (multi-model consensus with a usage estimate)
- Flag rules, JSON run-report schema, task-writing guide, templates
- Claude Code plugin + marketplace manifests
- Safety: credentials from env var, prompt-injection guard in the tester, test-environment guidance
