# Flag rules

Compute these per run from the tester JSON plus your own `verified_success`. Then aggregate per task.

## Per-run flags

| Flag | Condition | Severity |
|---|---|---|
| `TASK_FAILED` | `verified_success == false` | critical |
| `FALSE_SUCCESS` | `claimed_success == true` and `verified_success == false` | critical (the user thinks it worked and it didn't) |
| `NO_CONFIRMATION` | `verified_success == true` and `confirmation_seen == false` | major |
| `BROKEN` | `stop_reason == "broken"` | critical |
| `INEFFICIENT_PATH` | `steps_taken / optimal_steps > 1.5` (success runs only) | minor if ≤ 2.0, major if > 2.0 |
| `BACKTRACK` | a "go back", closing a panel without acting, or returning to a previously visited URL/screen without progress | minor each; major if ≥ 2 in one run |
| `WRONG_TURN` | `matched_expectation == false` on a step | minor each; major if ≥ 3 in one run |
| `HESITATION` | `hesitation` lists ≥ 2 options **and** `confidence ≤ 2` | minor; major if it precedes a WRONG_TURN |
| `UNCLEAR_LABEL` | `confusion` is set and quotes a UI label, icon or term | minor; major if repeated across runs |
| `UNHELPFUL_ERROR` | `error_seen` is set and the tester says they didn't know how to fix it, or the next step is not a fix | major |
| `DISCOVERABILITY` | `stop_reason == "stuck"` and `where_i_expected_it` is set | critical (record where they looked: that's the fix hint) |
| `LOW_EASE` | `overall_ease ≤ 2` on a run that succeeded | minor |

## Aggregation per task

- **Success rate** = verified successes / runs.
- **Median efficiency** = median(steps_taken / optimal_steps) over successful runs.
- A flag becomes a **finding** if:
  - it occurs in ≥ 2 of 3 runs (or ≥ 40% of runs when N ≠ 3), **or**
  - it is `critical` and occurs at least once.
- Merge findings that point to the same UI element or step (e.g. three HESITATION flags on the same sidebar menu = one finding, with the run count).
- Findings that appear in only one run and are not critical → list them under "Weak signals", no fix required.

## Finding format (report.json)

```json
{
  "task_id": "add-employee",
  "flag": "DISCOVERABILITY",
  "severity": "critical",
  "runs_affected": "3/3",
  "where": "Sidebar / Team page",
  "evidence": [
    {"run": 1, "step": 4, "expected": "An 'Add' button near the staff list", "observed": "Only a search field and filters"},
    {"run": 2, "step": 6, "quote": "I don't see how to add someone, maybe it's in settings?"}
  ],
  "proposed_fix": "Move 'Nouvel employé' from the overflow menu (⋯) to a primary button above the list."
}
```

## Other modes

- **lite-check**: there is one run per task, so skip run aggregation. Only `critical` flags become findings; everything else goes under "To confirm with a standard test". In lite reports the compact steps may lack `expected`/`observed`. Base `WRONG_TURN` and `HESITATION` only on the steps that have the full fields.
- **panel**: aggregate across tester profiles with the consensus table in `modes.md` instead of the run threshold above.

## Verdict

- **PASS**: every task has success rate ≥ 2/3 and there are no critical findings.
- **NEEDS WORK**: anything else.
- **LITE OK** (lite-check only): no critical findings. Never report `PASS` from a lite check.
