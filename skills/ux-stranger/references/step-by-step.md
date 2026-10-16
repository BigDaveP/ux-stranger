# Step-by-step workflow (default when a human is present)

Instead of testing everything in one shot, work in short rounds:

```
1. Map the app        → ux-stranger/map.yaml
2. Human picks        → module(s) / flow(s) + mode
3. Draft tasks        → human approves or edits
4. Run the test      → only those tasks
5. Report             → human picks: fix now / next module / stop
```

Each round costs only what the human chose. The map persists, so later sessions resume where the last one stopped.

## Invocation

| Command | Behavior |
|---|---|
| `/ux-stranger` | Step-by-step. Map (or reuse the map), then ask what to test |
| `/ux-stranger map` | Build or refresh the map only, then stop |
| `/ux-stranger <module or flow id>` | Skip to step 3 for that module/flow (build the map first if missing) |
| `/ux-stranger all` | One-shot: every high-priority flow, no questions (old behavior) |
| `lite-check` / `panel` | Combine with any of the above, e.g. `/ux-stranger lite-check billing` |

**No human in the loop** (CI, scheduled run, automated PR pipeline): don't ask questions. Use one-shot on modules flagged `changed: true` in the map, or on all high-priority flows if git info is unavailable. State that choice at the top of the report.

## 1. Map the app

You are the builder: you may use the code here. Discovery is not the test. Keep it cheap:

1. **Reuse first.** If `ux-stranger/map.yaml` exists and is less than ~2 weeks old, only refresh `changed` flags and add new routes.
2. **Routes from code.** Read the router (e.g. Next.js `app/` or `pages/`, React Router config, Laravel/Rails routes). Don't open every component.
3. **Navigation as users see it.** Open the running app once, logged in, and read the main navigation (one snapshot, one screenshot). Group modules the way the nav groups them, not the way the code does.
4. **What changed.** `git diff --name-only <main branch>...HEAD` (or the last commits) → mark modules whose routes or components changed.
5. **Flows per module.** For each module, list 1–5 user jobs as verbs in user language ("Add an employee", "See last week's sales"). Don't list every button.
6. **Priority** per flow:
   - `high`: primary job of the module, touches money, data deletion or anything irreversible, onboarding/first use, or changed in this branch.
   - `medium`: frequent secondary job.
   - `low`: rare settings and edge cases.

In `lite-check`, skip step 3 (code + git only).

Write `ux-stranger/map.yaml` (template: `templates/map.example.yaml`). Keep the `last_result` fields from the previous map.

## 2. Let the human pick

Show a compact numbered overview **in the chat** (not only in `map.yaml`), with high-priority and changed flows first:

```
Modules found: 6 · flows: 19 · changed in this branch: 2

 #  Module          Flows  Priority  Changed  Last result
 1  Équipe            4    high      ●        —
 2  Horaires          5    high               NEEDS WORK (Oct 12)
 3  Ventes            3    medium    ●        —
 4  Paramètres        4    low                —
 …
Suggested: 1 (changed + never tested), 2 (still failing).
```

Then ask, with the host's question tool if it has one (multiple-choice), otherwise in plain chat, and **wait**:

- **What to test?** A module (all its high/medium flows), specific flows (`1.2, 3.1`), or "suggested".
- **Which mode?** lite-check / standard / panel. Pre-select whatever was passed in the command. Otherwise suggest lite-check for a first look and standard for changed modules.

Show the cost of the choice in one line (number of tasks × runs = browser sessions) so the human picks knowingly.

## 3. Draft tasks, get approval

For the chosen flows, write the tasks following `writing-tasks.md` (goal in user words, persona, hidden success_check, optimal_steps). Show them **in the chat** as a numbered table: #, goal, persona, optimal steps. Don't show success checks unless asked.

Ask: **run as is / edit / drop some**. Apply edits, then add the tasks to `ux-stranger/tasks.yaml`, each with `module:` and `flow:` set to the map ids (replace older tasks for the same flow). On the next round for that module, reuse them instead of redrafting.

## 4. Run

Run the test as described in `SKILL.md` steps 2–3, with the chosen mode, on the approved tasks only.

## 5. Report and next move

Write the report for this round (`ux-stranger/reports/<date>-<module>.md` + `.json`) and update `last_result` and `last_tested` in the map.

Then **show the report in the conversation before asking anything**. The human must be able to decide without opening a file. Print the summary as a normal chat message, in the same turn and **before** the question. In hosts where text between tool calls gets collapsed or summarized, use the host's "message to user" tool if it has one. Use this format, in the human's language:

```markdown
## UX Stranger — Contact · NEEDS WORK
**11/12 essais réussis** · mode standard · 4 tâches × 3 passes · [rapport complet](ux-stranger/reports/2026-10-16-contact.md)

| Tâche | Réussite | Étapes (médiane / optimal) |
|---|---|---|
| Envoyer une demande de soumission | 2/3 ⚠️ | 9 / 6 |
| Trouver le numéro de téléphone | 3/3 | 3 / 2 |

### Problèmes trouvés
| # | Gravité | Où | Problème | Correctif proposé | Essais |
|---|---|---|---|---|---|
| 1 | 🔴 critique | Bandeau de témoins | Cache le bouton « Envoyer » sur mobile | Bandeau compact en bas, sans masquer le contenu | 3/3 |
| 2 | 🟠 majeur | Formulaire | « Sans engagement » n'apparaît qu'après l'envoi | Afficher la mention au-dessus du bouton | 2/3 |
| 3 | 🟠 majeur | Formulaire | Téléphone obligatoire, le testeur voulait écrire par courriel | Accepter courriel OU téléphone (+ option « Rappelez-moi ») | 2/3 |
| 4 | 🟡 mineur | Services | Services listés après la section équipe | Mettre les services en premier | 3/3 |

> « Je cherche le bouton pour envoyer mais il y a une bannière par-dessus… » (essai 2, étape 5)

Signaux faibles : 2 (dans le rapport complet).
```

Rules:
- **Number findings once and reuse the same numbers in the question.** An option like "Fix 1, 2 and 4" is only allowed if 1, 2 and 4 are visible just above it.
- One line per finding, max ~8 rows. If there are more, show the critical and major ones and link the rest.
- Include at most 1–2 short tester quotes: the most telling ones.
- Say when a fix touches more than the UI (API, validation, data), so the human sees the scope before choosing.
- The full `.md`/`.json` report is still written. The chat summary is a view of it, not a replacement.

Then ask:

- **Fix now**: apply fixes for the findings the human selects (by number, e.g. "1, 2, 4" or "all"), then re-run only the affected tasks (cycle limits per mode still apply).
- **Next module**: back to step 2, with the overview updated.
- **Stop**: leave the map and reports for a later session.
