# Privacy

UX Stranger is a set of instructions (a skill) and a sub-agent definition. It has no server, no account, no analytics and no telemetry. The author receives no data from your use of it.

## What happens when you use it

- **Your app.** The tester opens the URL you provide in a local browser driven by Playwright MCP (declared by the Claude Code plugin, or configured by you; it is downloaded from npm and runs on your machine or session container) and types only the task data and the test credentials you supply.
- **Your model provider.** The tester runs on the model provider of the agent you already use (for example Claude in Claude Code). What it sees on screen is processed by that provider under that provider's own terms and privacy policy.
- **Panel mode (optional).** If you choose panel mode and have the Codex or Cursor CLI installed and logged in, the task brief and tester prompt are sent to that vendor through its CLI, under its own terms. The skill asks before running a panel.
- **Local files.** Maps, tasks, positioning (comprehension mode: your target personas and intended message) and reports are written only to your project (`ux-stranger/`). The tester never receives the positioning file, only a persona description. Reports can quote what was on screen. The bundled browser server saves screenshots and page snapshots in `ux-stranger/.playwright-mcp/`. Use test data, and add `ux-stranger/reports/` and `ux-stranger/.playwright-mcp/` to `.gitignore`.
- **Credentials.** Read from an environment variable you set (`UX_STRANGER_CREDENTIALS`), used only to log into the app under test, and never written to reports. Use a test account.

## Contact

Questions: [open an issue](https://github.com/BigDaveP/ux-stranger/issues).