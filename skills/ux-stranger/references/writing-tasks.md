# Writing unbiased tasks

The task text is the most common way to ruin a test. If the goal contains the path, you measure reading comprehension, not usability.

## The goal

Describe the **outcome the user wants**, in the user's vocabulary, with the concrete data they would have in their head.

| Bad (leaks the UI) | Good (user intent) |
|---|---|
| Click "Ajouter un employé" in the Équipe tab | Julie Martin starts Monday at the Plateau location as a server. Get her set up. |
| Use the date filter to show last week's sales | How much did the Plateau location sell last week? |
| Open Settings > Notifications and disable SMS | You're getting too many text messages from the app. Make them stop. |
| Export the CSV from the Reports page | Your accountant wants last month's payroll numbers in a spreadsheet. |

Checklist before saving a goal:
- [ ] No word that appears verbatim as a button, tab, menu item or page title. Use synonyms or describe the need.
- [ ] No route, component, or technical term (modal, dropdown, toggle, CRUD, endpoint).
- [ ] Contains the concrete data needed (names, dates, amounts) so the tester doesn't invent it.
- [ ] One outcome per task. Split "create X and then share it" unless the flow is meant to be continuous.
- [ ] Achievable in the current build. A goal the product can't satisfy measures nothing.

## Personas

Short, behavioral, relevant to the product. 1–2 sentences. Vary them across runs or tasks.

- "Restaurant manager, 45, uses a phone and a few apps daily, impatient between services, doesn't explore menus."
- "New office admin, comfortable with Google Workspace, careful, reads labels before clicking."
- "Owner checking numbers late at night on a laptop, wants answers in under a minute."

Avoid personas that make success trivial ("tech-savvy power user") unless that is the real audience.

## success_check (hidden from the tester)

Something **you** can verify objectively after the run:
- Database/API state: "employee 'Julie Martin' exists with location=Plateau, role=server, start_date=next Monday".
- UI state: "Notifications page shows SMS off for current user".
- Answer correctness: "tester's final answer contains $12,480 (±1%)". For information-finding tasks, add `"answer_required": true` and the tester's `hardest_moment`/final step must contain the answer.

## optimal_steps

Count the shortest path yourself using the step definition in `tester-prompt.md` (each click, each field typed, each select, each scroll needed). Be honest. Inflating it hides inefficiency.

## Coverage

- 3–8 tasks per test. Start with the primary job of the screen, then the most frequent secondary jobs, then one error-recovery task (e.g. "you made a typo in Julie's start date — fix it").
- Include at least one task that starts from a **different** entry point than the one you designed for (e.g. from the home dashboard rather than the feature page).
