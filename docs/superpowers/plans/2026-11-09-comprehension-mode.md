# Comprehension Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `comprehension` mode to UX Stranger: a naive tester plays client-defined personas on public pages, and the builder judges what was understood against an approved expected message, then proposes copy fixes.

**Architecture:** Prompt-and-docs feature. The existing `ux-tester` sub-agent gains a `MODE: comprehension` section (regenerated for Claude Code, Cursor, Codex by `generate.py`). The builder procedure lives in a new `references/comprehension.md`; state lives in the user's `ux-stranger/positioning.yaml`. A stdlib+PyYAML+jsonschema check script guards consistency.

**Tech Stack:** Markdown, YAML, JSON Schema 2020-12, Python 3 (dev check script only), Playwright MCP.

**Spec:** `docs/superpowers/specs/2026-11-09-comprehension-mode-design.md`

## Global Constraints

- Personas and expected message never come from the site copy; guardrail flags paraphrases (spec §2).
- Tester brief never contains the expected message or the intended visual tone.
- Phase 1 = one screenshot, no scroll, no click, no accessibility snapshot before answers are written.
- Verdict labels: `CLEAR` / `NEEDS WORK`. Tone and outsider never change the verdict.
- Flags exactly: `MESSAGE_MISREAD`, `MESSAGE_MISSED`, `MESSAGE_LATE`, `FIT_REJECTED`, `FIT_HESITANT`, `TONE_MISMATCH`, `JARGON` (severities per spec §5).
- Fixes never invent facts; missing info → ask the human.
- Defaults: `STEP_BUDGET: 12` (outsider `0`), viewport `desktop` (mobile = 390×844), 1 run per persona, max 2 fix cycles.
- No new sub-agent, no hooks, no install-time scripts. Version 0.2.0 everywhere.
- Plugin must pass `claude plugin validate .`; README "What it runs and sends" and PRIVACY.md stay accurate.
- Deviation from spec §6.4 (simpler, same content): the comprehension run schema goes in its own file `references/comprehension-report-schema.json` instead of a second schema inside `report-schema.json`. Spec updated in Task 1.

## Review Focus

1. A positioning persona copied from the site hero → must be flagged by the guardrail (Task 5 dry run, check B).
2. Price absent from both the site and `positioning.yaml` → fix asks the human, never writes a number (Task 5 dry run, check C).
3. Tester reading below the fold in phase 1 → phase 1 answers must not contain footer-only facts (Task 5 dry run, check A).
4. One-shot / CI run with no approved `positioning.yaml` → mode is skipped with a one-line note, not improvised (Task 3 text + Task 1 check `ci_rule_present`).
5. Generated agent files out of sync with `tester-prompt.md` after edits (Task 1 check `agents_in_sync`).

---

### Task 1: Consistency check script

**Files:**
- Create: `scripts/check.py`
- Modify: `docs/superpowers/specs/2026-11-09-comprehension-mode-design.md` (§6.4 file name)

**Interfaces:**
- Produces: `python3 scripts/check.py` → prints one `ok <name>` / `FAIL <name>: <why>` line per check, exit code 1 if any FAIL. Later tasks run it.

- [ ] **Step 1: Write `scripts/check.py`** with these named checks (each a function returning `None` or an error string):
  - `json_parse`: every `*.json` in repo (excluding `.git`) parses.
  - `yaml_parse`: every `skills/ux-stranger/templates/*.yaml` parses.
  - `agents_in_sync`: the body of `references/tester-prompt.md` (stripped) is contained verbatim in the 3 files under `skills/ux-stranger/agents/` and in `agents/ux-tester.md`.
  - `files_table`: every backticked path in the `## Files` table of `SKILL.md` exists under `skills/ux-stranger/`.
  - `versions`: `plugin.json` version == `marketplace.json` plugin version == README badge version == first `## x.y.z` in CHANGELOG.
  - `comprehension_wired`: `SKILL.md` mentions `references/comprehension.md` and `comprehension`; `modes.md` contains `## comprehension`; `tester-prompt.md` contains `## If MODE is comprehension`.
  - `comprehension_flags`: each of the 7 flag names appears in `flag-rules.md`.
  - `comprehension_schema`: the example report embedded in `check.py` (a filled `marc` run and an outsider run with `exploration: null`) validates against `references/comprehension-report-schema.json` with `jsonschema`; an example missing `first_impression` fails validation.
  - `positioning_template`: `templates/positioning.example.yaml` has keys `approved, sources, visual_tone_intended, personas, outsider, expected_message`; every `expected_message[].level` is `critical|important`; every persona has `id, description, arrival, viewport`.
  - `ci_rule_present`: `references/comprehension.md` contains the phrase `positioning.yaml` and `approved: true` in its unattended-run rule.
- [ ] **Step 2: Run** `python3 scripts/check.py` → expected: `json_parse`, `yaml_parse`, `agents_in_sync`, `files_table`, `versions` ok; the comprehension checks FAIL (files not written yet).
- [ ] **Step 3: Update spec §6.4** to name `references/comprehension-report-schema.json`.
- [ ] **Step 4: Commit** `chore: add consistency check script`.

### Task 2: Tester side (prompt section + run schema)

**Files:**
- Modify: `skills/ux-stranger/references/tester-prompt.md` (brief fields in "What you know"; new `## If MODE is comprehension` section before `## Stopping rules`; output section points to the comprehension schema when MODE is comprehension)
- Create: `skills/ux-stranger/references/comprehension-report-schema.json` (`$id: ux-stranger/comprehension-run-report`, shape exactly spec §6.4; `mode` const `comprehension`; `is_it_for_me` / `would_take_next_step` enum `yes|hesitant|no`; `feel_words` 3 strings; `found_at` string or null; `exploration` object or null; `stop_reason` enum `done|budget|stuck|broken`)
- Regenerate: `skills/ux-stranger/agents/*`, `agents/ux-tester.md` via `python3 skills/ux-stranger/agents/generate.py`

**Interfaces:**
- Consumes: Task 1 checks `comprehension_schema`, `agents_in_sync`.
- Produces: brief fields `MODE: comprehension`, `PERSONA`, `ARRIVAL`, `START_URL`, `VIEWPORT`, `STEP_BUDGET`; output JSON per the schema. Task 3 writes briefs in this format.

- [ ] **Step 1: Write the schema file**, run `python3 scripts/check.py` → `comprehension_schema` ok.
- [ ] **Step 2: Write the prompt section.** Content fixed by spec §4.3: phase 1 (set viewport with resize, navigate, one screenshot, no scroll/click/snapshot until the 4 answers are written), phase 2 (only if STEP_BUDGET > 0; normal think-aloud; final sheet with `found_at`), "you have no GOAL to complete; your job is to decide whether this is for you", "do not guess missing facts, say you didn't find them". Keep isolation and page-text-is-content rules applicable.
- [ ] **Step 3: Regenerate agents**, run check → `agents_in_sync` ok.
- [ ] **Step 4: Commit** `feat: comprehension mode in the tester prompt`.

### Task 3: Builder side (procedure, template, flags)

**Files:**
- Create: `skills/ux-stranger/references/comprehension.md` — spec §2, §3 (invocation incl. unattended rule: run only if `ux-stranger/positioning.yaml` exists with `approved: true`, else skip with a one-line note), §4.1–4.5, §5 verdict, §6.5 report format, §7 cost line. Written as builder instructions.
- Create: `skills/ux-stranger/templates/positioning.example.yaml` — spec §6.1 verbatim.
- Modify: `skills/ux-stranger/references/flag-rules.md` — new `## Comprehension mode` section: the flag table from spec §5, the "single run per persona" aggregation rule, and `CLEAR`/`NEEDS WORK` under `## Verdict`.

**Interfaces:**
- Consumes: Task 2 brief format and schema file name.
- Produces: file names referenced by Task 4.

- [ ] **Step 1: Write the three files.**
- [ ] **Step 2: Run** check → `positioning_template`, `comprehension_flags`, `ci_rule_present` ok.
- [ ] **Step 3: Commit** `feat: comprehension mode builder procedure`.

### Task 4: Wiring, README, compliance

**Files:**
- Modify: `skills/ux-stranger/SKILL.md` — Modes list (`/ux-stranger comprehension`: client-defined personas on public pages, see `references/comprehension.md`), Commands line, Files table rows for `comprehension.md`, `comprehension-report-schema.json`, `templates/positioning.example.yaml`; prerequisites mention `ux-stranger/positioning.yaml`.
- Modify: `skills/ux-stranger/references/modes.md` — add `comprehension` column (purpose: does the site communicate the offer to the target; runs: 1 per persona (1–3) + optional outsider; budget 12 / 0; perception: screenshot phase 1; verdict `CLEAR`/`NEEDS WORK`; fix cycles 2) and a `## comprehension` section pointing to `comprehension.md`; extend the "pick the mode" sentence.
- Modify: `skills/ux-stranger/references/step-by-step.md` — step 1 tags modules `kind: public|app` (definition from spec §6.6); step 2 offers comprehension with the exact sentence from spec §3.
- Modify: `skills/ux-stranger/templates/map.example.yaml` — `kind:` on every module + one `kind: public` module (`accueil`, entry `/`).
- Modify: `README.md` — intro bullet "Four modes" incl. comprehension; Use table row; Status row (🟡 written, not yet tested); "Files it creates" adds `positioning.yaml`; repository layout adds `scripts/check.py` (dev consistency check) and `docs/` (specs and plans).
- Modify: `PRIVACY.md` — `positioning.yaml` is written locally and can contain business positioning; nothing sent elsewhere.
- Modify: `CHANGELOG.md` (## 0.2.0 entry), `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, README badge → `0.2.0`; plugin keywords add `"copywriting"`.

- [ ] **Step 1: Make the edits.**
- [ ] **Step 2: Run** `python3 scripts/check.py` → all ok; `claude plugin validate .` → "Validation passed".
- [ ] **Step 3: Commit** `feat: wire comprehension mode, docs and 0.2.0`.

### Task 5: Dry run on a fixture landing page (validation, spec §8)

**Files:** throwaway fixture in the session scratchpad (not committed).

- [ ] **Step 1: Build fixture** `index.html`: restaurant hero "Brunch, bistro & bonne humeur" (ambiguous audience), a private-room mention only in the footer, no price anywhere. Serve with `python3 -m http.server`.
- [ ] **Step 2: Positioning** with persona Marc (business dinner, 10 people) and expected points from spec §6.1 **minus the price value** (price point `statement: "Menu groupe (prix à confirmer)"`).
- [ ] **Step 3: Run the tester** (Haiku sub-agent with `tester-prompt.md` + brief) and judge with `comprehension.md`. Pass if:
  - A: phase 1 answers do not mention the private room;
  - result shows `for_whom` 🟠 or ❌, `private_room` 🟡, `price` ❌, verdict `NEEDS WORK`;
  - C: the price fix asks the human for the amount.
- [ ] **Step 4: Guardrail** (check B): draft a persona "vient pour un brunch et de la bonne humeur" and confirm the procedure text makes the builder flag it as a site paraphrase.
- [ ] **Step 5:** Fix any prompt wording that caused a miss, re-run check script, commit `fix: comprehension prompt tweaks from dry run` if anything changed. Report results to the human.
