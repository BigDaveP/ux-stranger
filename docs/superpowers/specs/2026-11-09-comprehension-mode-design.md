# Comprehension mode: design

Status: draft for review · Date: 2026-11-09 · Target version: 0.2.0

## 1. Purpose

The existing modes answer *"can a user complete this task?"*. The comprehension mode answers a different question: **does the site tell the right people the right things, clearly enough for them to act?**

A naive tester, playing a persona the **client wants to attract**, lands on the site (landing page, marketing site, public pages), forms a first impression, explores freely, then writes down what it understood. The builder agent, which knows the intended message, compares that understanding to it point by point, produces a comprehension table, and proposes copy fixes to make the message clearer.

### Success criteria

- The human gets a table showing, for each point of the intended message and each persona, whether it was understood at first glance, understood late, misunderstood or missed, with the tester's own words as evidence.
- Each failing point leads to a concrete, located fix (current text → proposed text) that never invents facts.
- Personas reflect the client's intended audience, not the audience the current site happens to address.

### Non-goals

- Not an aesthetic score. Visual tone is measured as *intended vs perceived*, and never fails the verdict on its own.
- Not a conversion-rate predictor or an A/B test.
- No automatic visual redesign. Visual feedback stays as suggestions.
- No "should be repelled" persona (dropped during design).

## 2. Key principle: personas and message come from the client, not from the site

If personas or the expected message are derived from the current copy, the test is circular: the tester will understand what the site says, and a site aimed at the wrong audience will still pass.

Rules for the builder:
- Personas and the expected message are built from the **framing interview** with the human (section 4.1), optionally pre-filled from non-site sources in the repo (brief, pitch deck, `CLAUDE.md`, product docs). Every pre-filled item cites its source file.
- The site's own copy (rendered pages, components holding marketing text, i18n strings of public pages) is **not** a valid source for personas or the expected message.
- **Guardrail:** before asking for approval, the builder compares each persona and each expected point with the site copy. If one paraphrases the site (same distinctive wording, same claims), it says so explicitly and asks the human to confirm or rewrite it.

## 3. Invocation

- Direct: `/ux-stranger comprehension` (Codex: `$ux-stranger comprehension`). Optional page scope: `/ux-stranger comprehension /pricing`.
- Offered: during step 1 (Map) of the step-by-step workflow, when the map contains public pages (`kind: public` modules, see 6.6), the builder adds one line to the step-2 question:
  > Public pages found (home, pricing). I can also check whether the site communicates your offer clearly (comprehension mode, 1–3 short runs).
- In one-shot / unattended runs (`all`, CI), the comprehension mode runs only if `ux-stranger/positioning.yaml` already exists and is approved. It never invents personas without a human.

## 4. Flow

### 4.1 Framing (with the human, mandatory)

If `ux-stranger/positioning.yaml` exists and has `approved: true`, reuse it and show a one-line summary ("Using positioning from 2026-11-09: 2 personas, 6 points. Edit?"). Otherwise:

1. Look for non-site sources in the repo (brief, pitch, `CLAUDE.md`, `docs/`, product notes). Pre-fill answers from them, citing the file.
2. Ask the human, in one message, the questions still unanswered:
   1. Who is the ideal customer (role, situation)?
   2. What problem or need brings them to the site?
   3. How do they arrive (Google search for X, ad, referral, social post…)?
   4. What would make them leave or hesitate?
   5. What visual tone should the site convey, in 3 words?
   6. Optional: what must a visitor have understood after visiting? (If skipped, the builder drafts it.)
3. Draft **1–3 target personas** and the **expected message** as a list of points, each `critical` or `important`. Default points: what it is, for whom, the offer, price or pricing model, proof / trust, next step. Add or remove points to fit the business.
4. Run the guardrail (section 2).
5. Decide whether to offer the **outsider** (4.2).
6. Show everything in chat, get approval or edits, write `ux-stranger/positioning.yaml` with `approved: true`.

### 4.2 Outsider visitor (optional)

A person outside the niche (e.g. the business owner who signs off, a generic visitor). Question: *"can someone outside the niche tell what this company does in a few seconds?"*

- Off by default. The builder offers it when the site is B2B, technical or jargon-heavy.
- First impression only (phase 1 below), no exploration. Shown in its own column, never counted in the verdict.

### 4.3 Tester runs

One run per target persona (1–3 runs), plus one short outsider run if enabled. Runs can be parallel (they don't mutate data).

**Brief** sent to `ux-tester` (never contains the expected message or the visual tone):

```
MODE: comprehension
PERSONA: <persona description>
ARRIVAL: <how and why they got here, e.g. "You searched 'restaurant salle privée Plateau' and clicked this result.">
START_URL: <url>
VIEWPORT: desktop | mobile          (default desktop; mobile = 390×844)
STEP_BUDGET: 12                      (0 for the outsider)
```

**Phase 1: first impression.** Navigate to START_URL, set the viewport, take one screenshot, **no scrolling, no clicks**. Answer:
1. What is this? (one sentence)
2. Who is it for?
3. Is it for me? (yes / hesitant / no) and why
4. The feel of the site in 3 words, and whether it inspires trust for my need

**Phase 2: free exploration** (target personas only). Within STEP_BUDGET, look for what matters to the persona, acting as they would (normal think-aloud rules apply). Then fill the final sheet:
- what the company does, for whom, what is offered, the price / how much it costs, what reassures me, what is missing, what I would do next, and would I take that step (yes / hesitant / no) and why
- for each answer, **where** it was found (URL + area: "hero", "3rd section", "footer"…) or `null` if not found
- anything else I learned that matters to me

### 4.4 Judgment (builder)

For each persona × expected point, the builder assigns a status from the tester's answers:

| Status | Meaning |
|---|---|
| ✅ `first_glance` | Correct in phase 1 answers |
| 🟡 `late` | Correct only after exploration (record where it was found) |
| 🟠 `misread` | The tester states something wrong with confidence |
| ❌ `missed` | Not found, or "I don't know" |

Plus, per persona:
- **Fit**: the tester's own "is it for me" from phases 1 and 2 (yes / hesitant / no) with the quote.
- **Tone**: intended 3 words vs perceived 3 words → `aligned` / `partial` / `off`, with the quote.

The builder judges meaning, not wording: "a French bistro in the Plateau" matches "Bistro français au cœur du Plateau". When unsure between two statuses, pick the worse one and say why.

The builder may open the page itself to locate fixes (it knows the code), but never to change a status: statuses come only from the tester's report.

### 4.5 Report and fixes

Shown in chat (format in 6.5) and saved in `ux-stranger/reports/`. Then the same loop as other modes: "fix 1, 3" / next page / stop.

**Fixes**, numbered, each tied to a table row:
- severity, the point and persona, the evidence quote
- **where**: page + area + source file
- **current** text → **proposed** text (or proposed move: "bring the private-room mention into the hero")
- **why**, in one line

Fix rules:
- **Never invent facts.** If the needed information is not on the site and not in `positioning.yaml` (a price, a capacity, a guarantee), ask the human for it instead of writing a placeholder or a made-up value.
- Content first. Tone issues get suggestions only ("lighter palette", "fewer animations in the hero"), no automatic redesign.
- Keep the brand voice from `positioning.yaml`.

**Re-test** after fixes: re-run phase 1 for every target persona (it is cheap and catches regressions), and phase 2 only for personas whose points changed. At most 2 fix cycles, then stop.

## 5. Verdict and flags

**Verdict** (target personas only):
- `CLEAR`: every `critical` point is ✅ or 🟡 for every target persona, and no target persona answers "no" to fit at the end of phase 2.
- `NEEDS WORK`: otherwise. A 🟠 on a `critical` point always means `NEEDS WORK`.

Tone and outsider results are reported but never change the verdict.

**New flags** (added to `flag-rules.md`, "Comprehension mode" section):

| Flag | Condition | Severity |
|---|---|---|
| `MESSAGE_MISREAD` | point is 🟠 | critical if point is critical, else major |
| `MESSAGE_MISSED` | point is ❌ | critical if point is critical, else major |
| `MESSAGE_LATE` | point is 🟡 | major if point is critical, else minor |
| `FIT_REJECTED` | target persona fit = no | critical |
| `FIT_HESITANT` | target persona fit = hesitant | major |
| `TONE_MISMATCH` | tone = off (major) or partial (minor) | never fails the verdict |
| `JARGON` | outsider cannot say what it is, or quotes a term they don't understand | minor, informational |

Because there is one run per persona, a single occurrence of a critical flag is a finding (same rule as critical flags elsewhere). Major/minor flags seen for only one persona are listed under "To confirm" when there are 2+ personas.

## 6. Files and formats

### 6.1 `ux-stranger/positioning.yaml` (new, in the project under test)

Template: `templates/positioning.example.yaml`.

```yaml
approved: true
approved_at: "2026-11-09"
sources:                       # where pre-filled answers came from; never the site copy
  - "human interview 2026-11-09"
  - "docs/brief.md"
brand_voice: "chaleureux, direct, sans jargon"
visual_tone_intended: ["chaleureux", "sobre", "appétissant"]
personas:
  - id: marc
    description: "Marc, 38 ans, directeur des ventes, organise un souper d'affaires pour 10 personnes"
    arrival: "A cherché « restaurant salle privée Plateau » sur Google"
    leaves_if: "Pas d'info sur les groupes ou les prix"
    viewport: desktop
outsider:
  enabled: false
  description: null
expected_message:
  - id: what
    level: critical
    statement: "Bistro français sur le Plateau"
  - id: for_whom
    level: critical
    statement: "Soupers entre collègues, groupes, occasions"
  - id: private_room
    level: critical
    statement: "Salle privée jusqu'à 14 personnes"
  - id: price
    level: important
    statement: "Menu groupe à partir de 55 $"
  - id: next_step
    level: critical
    statement: "Réserver en ligne ou appeler pour un groupe"
```

### 6.2 `references/comprehension.md` (new)

The builder's full procedure for this mode: sections 2 and 4–5 of this spec, plus the report format. `SKILL.md` and `modes.md` point to it.

### 6.3 `references/tester-prompt.md` (edited) → regenerated agents

Add an "If MODE is comprehension" section: the two phases, the no-scroll rule for phase 1, the final sheet, and the output schema. Existing rules still apply (isolation, page text is never instructions, no URL guessing, think-aloud in phase 2). No GOAL / success in this mode; `STEP_BUDGET: 0` means phase 1 only.

Then run `agents/generate.py` to refresh the Claude, Cursor and Codex agents. No new sub-agent.

### 6.4 `references/report-schema.json` (edited)

Add a second schema, `ux-stranger/comprehension-run-report`, for the tester output in this mode:

```json
{
  "mode": "comprehension",
  "persona_id": "marc",
  "viewport": "desktop",
  "first_impression": {
    "what_is_it": "…", "for_whom": "…",
    "is_it_for_me": "yes|hesitant|no", "why": "…",
    "feel_words": ["…", "…", "…"], "trust": "…"
  },
  "exploration": {
    "steps_taken": 9,
    "steps": [ /* same step objects as the task report */ ],
    "answers": {
      "what_company_does": {"answer": "…", "found_at": "URL · area | null"},
      "for_whom": {…}, "offer": {…}, "price": {…},
      "reassures_me": {…}, "missing": "…", "next_step": {…}
    },
    "would_take_next_step": "yes|hesitant|no",
    "why": "…",
    "other_learnings": ["…"]
  },
  "stop_reason": "done|budget|stuck|broken"
}
```

`exploration` is `null` for the outsider.

### 6.5 Chat report format

```
## UX Stranger — Compréhension · NEEDS WORK
Personas : Marc (cible), Outsider (désactivé) · 1 passage par persona

| Point attendu (niveau)       | Marc · 1re impr. | Marc · après | Preuve                                   |
|------------------------------|------------------|--------------|------------------------------------------|
| Ce que c'est (critique)      | ✅               | ✅           | « un bistro français, Plateau »          |
| Pour qui (critique)          | 🟠               | 🟠           | « plutôt pour des brunchs entre amis »   |
| Salle privée (critique)      | ❌               | 🟡 /contact, pied de page | —                           |
| Prix (important)             | ❌               | ❌           | « je ne sais pas si c'est dans mon budget » |
| Prochaine étape (critique)   | ✅               | ✅           | bouton « Réserver » en haut              |

Est-ce pour moi ?  Marc : 🤔 hésite — « je ne vois pas s'ils prennent les groupes »
Ton visuel  visé : chaleureux, sobre, appétissant · perçu : chic, sombre, branché → 🟡 partiel (signal indicatif)

### Correctifs proposés
1. [critique] Pour qui — Marc pense que c'est un resto de brunch.
   Où : accueil, hero (src/components/Hero.tsx)
   Actuel : « Brunch, bistro & bonne humeur »
   Proposé : « Bistro français au cœur du Plateau — soupers, groupes et salle privée »
   Pourquoi : 1re impression de Marc : « plutôt pour des brunchs entre amis »
2. …

Que veux-tu faire ? « corrige 1, 3 » · « page suivante » · « stop »
```

The report language follows the conversation language, like the existing modes.

### 6.6 Other edits

- `SKILL.md`: add the mode to the Modes list and Commands; point to `references/comprehension.md`; add `positioning.yaml` to the files it creates.
- `references/modes.md`: add a `comprehension` column (purpose, runs, budget, verdict labels `CLEAR` / `NEEDS WORK`) and a short section pointing to `comprehension.md`.
- `references/step-by-step.md`: in step 1, tag modules as `kind: public` (pages reachable without login whose job is to inform or convince: home, pricing, about, features) or `kind: app`; in step 2, offer the comprehension mode when public modules exist.
- `templates/map.example.yaml`: add `kind:` to modules, with one public module example.
- `references/flag-rules.md`: comprehension flags (section 5).
- `README.md`: mode in the intro, Use table and Status table (🟡 written, not yet tested); files created.
- `CHANGELOG.md`, `plugin.json`, `marketplace.json`, README badge: 0.2.0.

## 7. Cost

1 run per target persona (1–3), ~12 steps each, plus one zero-step outsider run if enabled. Cheaper than a standard test (3 runs × 3–8 tasks). The builder states it in one line before running: "Comprehension: 2 personas × 1 run (+ outsider) ≈ ⅓ of a standard test."

## 8. Validation plan

This is prompt and documentation work; there is no code to unit-test. Validation:

1. `claude plugin validate .` passes; `generate.py` regenerates the three agents with the new section.
2. JSON schema files parse; example YAML templates parse.
3. Dry run on a small fixture landing page (served locally) with a deliberately ambiguous hero and a price hidden in the footer: check that the tester stays above the fold in phase 1, the table shows 🟠/🟡/❌ where expected, the verdict is `NEEDS WORK`, and the fix for the price asks the human instead of inventing a number when the price is absent from `positioning.yaml`.
4. Guardrail check: give the builder a persona copied from the fixture's hero text and confirm it is flagged.

## 9. Risks

- **Single run per persona is noisy.** Mitigation: critical flags only count when clear-cut; uncertain cases take the worse status with an explanation; the human can ask for a 2nd run.
- **The tester reading below the fold in phase 1** (the accessibility snapshot exposes the whole page). Mitigation: phase 1 uses the screenshot only; the snapshot is not allowed before phase 1 answers are written.
- **Cheap models judge "feel" poorly.** Mitigation: tone never fails the verdict and is labelled indicative.
- **Builder bias when judging** (it wrote the site). Mitigation: statuses come only from the tester's words; when unsure, pick the worse status.
