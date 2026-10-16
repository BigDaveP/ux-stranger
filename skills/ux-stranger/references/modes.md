# Test modes

Pick the mode from the invocation argument (`/ux-stranger`, `/ux-stranger lite-check`, `/ux-stranger panel`) or from the request wording ("quick UX check" → lite, "get a second opinion from several models" → panel). When unsure, use **standard**.

| | `lite-check` | standard (default) | `panel` |
|---|---|---|---|
| Purpose | Cheap smoke test on smaller plans | Normal check after a UI change | High-stakes flows, before release |
| Tasks | max 3, primary jobs only | 3–8 | 3–8 |
| Runs per task | 1 | 3 | 2 per tester profile (see below) |
| Tester profiles | 1 | 1 | 2–4 (model × persona) |
| Perception | accessibility snapshot first, screenshots only at checkpoints | screenshot every step | screenshot every step |
| Think-aloud | compact | full | full |
| STEP_BUDGET | `optimal_steps × 2` | `max(optimal × 3, optimal + 6)` | same as standard |
| Fix cycles | 1 re-check of failed tasks | up to 3 | up to 3 |
| Verdict labels | `LITE OK` / `NEEDS WORK` | `PASS` / `NEEDS WORK` | `PASS` / `NEEDS WORK` + agreement score |

## lite-check

Goal: catch blocking problems (can't find it, broken flow, false success) at a fraction of the usage. It is **not** a full usability verdict.

Builder rules:
- Choose at most 3 tasks: the primary job of the changed screen, plus up to 2 others. Skip error-recovery and alternate-entry-point tasks.
- Run tasks **one at a time** (no parallel testers), 1 run each.
- Pass `MODE: lite` in the tester brief (the tester prompt has a lite section).
- Only `critical` flags count as findings. Every `major`/`minor` flag goes under "To confirm with a standard test", with no fix required.
- After fixes, re-run only the tasks that failed, once. Then stop.
- Report verdict `LITE OK` (no critical findings), never `PASS`. Add one line: "Lite check: 1 run per task, low confidence on non-blocking issues. Run a standard test before release."

## panel

Goal: separate real interface problems from one model's quirks. Usage is several times standard. **Before running, show an estimate and ask for confirmation**:

```
Panel: [T] tasks × [P] tester profiles × [R] runs = [T×P×R] browser sessions
(standard mode would be [T×3]). Roughly [T×P×R ÷ (T×3)]× the usage of a standard test. Continue? (yes / switch to standard)
```

Skip the confirmation only if the user already said in this conversation that usage is not a concern.

### Building the panel

A **tester profile** = one model + one persona. Use 2–4 profiles and vary both:

1. **Models.** Use what is available natively, without API keys:
   - Claude Code: `ux-tester` (Haiku). Add a second Claude profile by spawning the same prompt on `sonnet` only if no other vendor is available. A stronger model finding a problem is still a strong signal.
   - Other vendors via CLIs **already installed and logged in** on the machine, called from the shell with the same brief and the content of `references/tester-prompt.md`:
     - Codex: `codex exec --model <mini model> "<prompt + brief>"`
     - Cursor: its agent CLI in non-interactive mode, if installed.
     Check `which codex` / the Cursor CLI first. If one is missing or not logged in, say so in one line and continue with the profiles you have. Never ask for API keys.
   - Each external tester needs its own browser MCP configured in that host (see `host-setup.md`).
2. **Personas.** Give each profile a different persona from the task file. If the file has only one, write a contrasting second one (e.g. hurried vs careful).

Run 2 runs per profile. Parallel is fine unless tasks mutate shared data.

### Consensus

Aggregate flags per task across **profiles**, not just runs. A profile "raises" a flag if it appears in ≥ 1 of its 2 runs.

| Profiles raising the flag | Status | Action |
|---|---|---|
| majority (≥ 2 of 3, 2 of 2, ≥ 3 of 4) | **Confirmed** | fix required |
| exactly half, or only the weaker model(s) | **Ambiguous** | fix if cheap; report the disagreement and quote both sides |
| one profile only | **Isolated** | list under weak signals |
| any `critical` flag raised by the strongest profile in the panel | **Confirmed** | fix required, whatever the others say |

Report an **agreement score** per task = share of profiles with the same verified outcome (all succeed or all fail). A low agreement on success is itself a finding: the flow works for some users and not others.
