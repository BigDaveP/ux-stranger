# Test modes

Pick the mode from the invocation argument (`/ux-stranger`, `/ux-stranger lite-check`, `/ux-stranger panel`, `/ux-stranger comprehension`) or from the request wording ("quick UX check" → lite, "get a second opinion from several models" → panel, "is my landing page clear?", "do visitors get what we do?" → comprehension). When unsure, use **standard**.

| | `lite-check` | standard (default) | `panel` | `comprehension` |
|---|---|---|---|---|
| Purpose | Cheap smoke test on smaller plans | Normal check after a UI change | High-stakes flows, before release | Does the site communicate the offer to the target personas? (public pages) |
| Tasks | max 3, primary jobs only | 3–8 | 3–8 | none: first impression + free exploration |
| Runs per task | 1 | 3 | 2 per tester profile (see below) | 1 per target persona (1–3, up to 5 on request) + outsider when the site is technical/B2B |
| Tester profiles | 1 | 1 | 2–4 (model × persona) | 1 |
| Perception | accessibility snapshot first, screenshots only at checkpoints | screenshot every step | screenshot every step | one screenshot for the first impression, then screenshot every step |
| Think-aloud | compact | full | full | full (exploration only) |
| STEP_BUDGET | `optimal_steps × 2` | `max(optimal × 3, optimal + 6)` | same as standard | 12 (outsider: 0) |
| Fix cycles | 1 re-check of failed tasks | up to 3 | up to 3 | up to 2 |
| Verdict labels | `LITE OK` / `NEEDS WORK` | `PASS` / `NEEDS WORK` | `PASS` / `NEEDS WORK` + agreement score | `CLEAR` / `NEEDS WORK` |

Comprehension is a different kind of test: no tasks, no success check. It applies to public pages (landing, home, pricing, marketing site), not logged-in screens.

## comprehension

Goal: check that the site tells the people the client wants to attract what it does, for whom, the offer, the price, why to trust it and what to do next, and propose copy fixes. Full procedure: `comprehension.md`. Key rules:
- Personas and the expected message come from the human (framing interview) or non-site documents, never from the site's copy. Flag any persona that paraphrases the site.
- The tester brief never contains the expected message or the intended tone.
- Tone and the optional outsider are reported but never change the verdict.

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
     - Codex: `codex exec --model gpt-6-luna "<prompt + brief>"` (Playwright MCP must be in `~/.codex/config.toml`).
     - Cursor: `agent -p --model <fast model id> --approve-mcps --output-format text "<prompt + brief>"`.
     Check `which codex` / `which agent` first, and `agent status` for Cursor's login. Headless Cursor runs may require an API key. If a CLI is missing, not logged in, or asks for a key, say so in one line and continue with the profiles you have. Never ask the human for API keys.
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