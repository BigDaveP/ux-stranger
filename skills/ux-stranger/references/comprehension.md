# Comprehension mode (builder procedure)

The task modes ask *"can a user complete this task?"*. This mode asks: **does the site tell the right people the right things, clearly enough for them to act?**

The tester plays a persona **the client wants to attract**. It lands on a public page, forms a first impression, explores, and writes down what it understood. You know the intended message. You compare, point by point, fill a comprehension table, and propose copy fixes.

Use it on public pages: landing, home, pricing, about, features, marketing sites. Not on logged-in app screens.

## 1. The rule that makes this test worth anything

**Personas and the expected message come from the client, never from the site.** If you derive them from the current copy, the tester will understand what the site says, and a site aimed at the wrong audience will still pass.

- Valid sources: the human (framing interview below), and non-site documents in the repo: a brief, pitch deck, `CLAUDE.md`, `docs/`, product notes. Cite the file for every pre-filled item.
- Not valid: rendered pages, components or i18n strings holding the public pages' marketing copy, meta descriptions, the README's tagline if it is copied from the site.
- **Guardrail.** Before asking for approval, compare each persona and each expected point with the site copy. If one paraphrases the site (same distinctive words, same claims, same audience as the hero describes), say so explicitly: *"Persona 2 repeats the hero ('brunch et bonne humeur'). Is this really who you want to attract, or is it what the site currently says?"* Get a confirmation or a rewrite. Never silently keep it.

## 2. Invocation

- `/ux-stranger comprehension` (Codex: `$ux-stranger comprehension`). Optional page scope: `/ux-stranger comprehension /pricing`. Default start page: the home page (`kind: public` module with entry `/`, or `base_url`).
- Offered by step-by-step mode: when the map has `kind: public` modules, add one line to the step-2 question (see `step-by-step.md`).
- **Unattended runs** (`all`, CI, no human): run this mode only if `ux-stranger/positioning.yaml` exists with `approved: true`. Otherwise skip it and add one line to the report: "Comprehension mode skipped: no approved positioning.yaml (needs a human once)." Never invent personas without a human.

## 3. Framing (with the human)

If `ux-stranger/positioning.yaml` exists with `approved: true`, reuse it. Show one line ("Using positioning approved on 2026-11-09: 2 personas, 6 points. Edit anything?") and go to step 4.

Otherwise:

1. Look for non-site sources (section 1). Pre-fill what you can, with the source file.
2. Ask the human, **in one message**, only the questions still open:
   1. Who is your ideal customer (role, situation)?
   2. What problem or need brings them to the site?
   3. How do they usually arrive (search for what, ad, referral, social post…)?
   4. What would make them leave or hesitate?
   5. What should the site feel like, in 3 words?
   6. Optional: what must a visitor have understood when they leave? (If skipped, you draft it.)
3. Draft **1–3 target personas**: who, situation, `arrival` (concrete: "searched 'restaurant salle privée Plateau' on Google"), `leaves_if`, `viewport` (`mobile` when that audience mostly browses on a phone, e.g. restaurants, local services).
4. Draft the **expected message** as points, each `critical` or `important`. Defaults: what it is, for whom, the offer, price or pricing model, proof / trust, next step. Add business-specific points (e.g. "private room up to 14"), remove what doesn't apply.
5. Run the guardrail (section 1).
6. **Outsider (optional, off by default).** Offer it when the site is B2B, technical or jargon-heavy: "Add an outsider (someone outside the niche) to check that the basics are understandable? +1 short run." It only does the first impression.
7. Show personas, points, tone and outsider choice in chat. On approval, write `ux-stranger/positioning.yaml` (template: `templates/positioning.example.yaml`) with `approved: true` and `approved_at`.

## 4. Run the testers

One run per target persona, plus one for the outsider if enabled. Runs can be parallel (nothing is mutated). Before running, one line: "Comprehension: [P] personas × 1 run (+ 1 short outsider run) = [P or P+1] browser sessions (a standard test is 9–24)."

Spawn `ux-tester` with this brief. **Never include the expected message, the intended tone, `leaves_if`, or anything from the repo.**

```
MODE: comprehension
PERSONA_ID: marc
PERSONA: Marc, 38, sales director, organizing a business dinner for 10 people next month.
ARRIVAL: You searched "restaurant salle privée Plateau" on Google and clicked this result.
START_URL: http://localhost:3000/
VIEWPORT: desktop
STEP_BUDGET: 12
```

Outsider: same brief with its own persona, `STEP_BUDGET: 0`.

Validate each report against `references/comprehension-report-schema.json`. If it doesn't parse or validate, re-run that persona once; if it fails again, report it as a tester failure, not as a site problem.

## 5. Judge

Statuses come **only from the tester's words**. You may open the site yourself to locate fixes, never to change a status.

For each target persona × expected point:

| Status | Rule |
|---|---|
| ✅ `first_glance` | The phase-1 answers (`first_impression`) state it correctly |
| 🟡 `late` | Correct only in `exploration.answers` or `other_learnings`; record `found_at` |
| 🟠 `misread` | The tester states something that contradicts the point, with confidence |
| ❌ `missed` | Not found, `answer: null`, or "I don't know" |

- Judge meaning, not wording: "a French bistro in the Plateau" matches "Bistro français au cœur du Plateau".
- When unsure between two statuses, pick the worse one and say why in the evidence column.
- If phase-1 answers mention something that is only visible further down the page, the tester broke phase 1: discard that run's first-impression column, mark it "first impression invalid", and judge from exploration only.

Per target persona, also:
- **Fit**: `first_impression.is_it_for_me` and `exploration.would_take_next_step`, with the `why` quote.
- **Tone**: intended words (positioning) vs `feel_words` → `aligned` (same register), `partial` (some overlap or neutral), `off` (opposite register, e.g. "flashy, cold" vs "warm, simple"), with the `trust` quote.

Outsider: only "what it is" and "for whom" from the first impression. If they can't say what it is, or quote a term they don't understand, raise `JARGON`.

Flags and verdict: `flag-rules.md`, section "Comprehension mode".

## 6. Report

Save `ux-stranger/reports/<date>-comprehension.md` + `.json` (the tester reports and your judgments). Then show this in chat, in the human's language, **before** asking anything:

```markdown
## UX Stranger — Compréhension · NEEDS WORK
Personas : Marc (cible) · Outsider désactivé · 1 passage par persona · [rapport complet](ux-stranger/reports/2026-11-09-comprehension.md)

| Point attendu (niveau) | Marc · 1re impression | Marc · après exploration | Preuve |
|---|---|---|---|
| Ce que c'est (critique) | ✅ | ✅ | « un bistro français, Plateau » |
| Pour qui (critique) | 🟠 | 🟠 | « plutôt pour des brunchs entre amis » |
| Salle privée (critique) | ❌ | 🟡 accueil · pied de page | — |
| Prix (important) | ❌ | ❌ | « je ne sais pas si c'est dans mon budget » |
| Prochaine étape (critique) | ✅ | ✅ | bouton « Réserver » en haut |

**Est-ce pour moi ?** Marc : 🤔 hésite — « je ne vois pas s'ils prennent les groupes »
**Ton visuel** visé : chaleureux, sobre, appétissant · perçu : chic, sombre, branché → 🟡 partiel *(signal indicatif)*

### Correctifs proposés
1. **[critique] Pour qui** — Marc pense que c'est un resto de brunch.
   Où : accueil, hero (`src/components/Hero.tsx`)
   Actuel : « Brunch, bistro & bonne humeur »
   Proposé : « Bistro français au cœur du Plateau — soupers, groupes et salle privée »
   Pourquoi : 1re impression de Marc : « plutôt pour des brunchs entre amis »
2. **[important] Prix** — introuvable. Le prix du menu groupe n'est ni sur le site ni dans le positionnement : **quel montant afficher ?**

Que veux-tu faire ? « corrige 1, 2 » · « autre page » · « stop »
```

With 2+ personas, add one pair of columns per persona. With an outsider, add one "Outsider · 1re impression" column filled only for "what it is" and "for whom".

## 7. Fixes

One numbered fix per failing row (✅ rows get none; 🟡 on an `important` point gets one only if cheap). Each fix: severity, point and persona, evidence quote, **where** (page, area, source file), **current → proposed** text (or a move: "bring the private-room line into the hero"), and **why** in one line.

- **Never invent facts.** If the fix needs information that is neither on the site nor in `positioning.yaml` (a price, a capacity, a guarantee, a delay), ask the human for it in the fix itself. Never write a placeholder or a plausible value.
- Content first. Tone issues get suggestions only ("lighter palette", "fewer animations in the hero"); no automatic redesign.
- Keep the `brand_voice` from `positioning.yaml`.
- Apply only the fixes the human picks.

**Re-test** after fixes: re-run phase 1 for every target persona (cheap, catches regressions) and full runs only for personas whose points changed. At most 2 fix cycles, then report what remains.

Update `positioning.yaml` only if the human changes the target or the message; record their answers to fact questions (e.g. the price) there so they are not asked twice.
