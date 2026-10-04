# Meesho reseller growth monitoring agent specification

## Goal

Keep category managers informed when category month-on-month revenue
moves beyond the 8% threshold, while requiring human approval before
any message is sent.

## Tools

- Part 1's SQL-generated `monthly_category_revenue.csv` supplies
  measured monthly revenue and order counts.
- Part 2's `validate_feed` checks the input before calculations.
- Part 2's `mom_growth` calculates the rounded percentage change.
- Part 2's `is_flagged` classifies each percentage.
- Part 3's `draft_flagged_category` fills the documented prompt
  structure offline, without an AI API or API key.
- Part 3's masking policy prevents raw reseller names in narratives
  that could be shared externally.

## Memory / State

For each run, the agent reads the previous month's revenue by category
from the validated Part 1 CSV. This is its comparison state; it does
not invent or estimate missing previous values. The output records the
run month, drafts, suppressed categories, escalations and errors.

## Planner: ordered subtasks

1. Load the monthly revenue feed and call `validate_feed`.
2. If validation fails, Hard Stop and surface the validation errors.
3. If valid, use `mom_growth` for every category against its previous
   month's revenue.
4. Call `is_flagged` for every computed percentage.
5. Sort flagged categories by absolute percentage change, descending.
6. Use Part 3's offline template to draft messages for at most the top
   three flagged categories. The cap prevents notification flooding.
7. Record other flagged categories as "suppressed, review manually";
   do not draft messages for them.
7b. Separately record exact-boundary categories in
    `escalated_categories`; do not draft for them. They are neither
    flagged nor not_flagged.
8. Emit exactly one structured JSON object for the run.

## Feedback loop and human approval

A drafted message is held for human approval. The runner records
`drafted_and_held_for_approval`; it does not send email or messages.
A manager must review a draft and approve any later distribution.
Suppressed and escalated categories require manual review.

## Guardrails

- **Input:** `validate_feed` must pass before MoM calculation or
  drafting. The runner validates the current input first.
- **Action:** Nothing is auto-sent. Drafting and holding are the
  runner's final action.
- **Output:** Every numeric figure in a draft must trace to the
  validated Part 1 feed or Part 2's `mom_growth`; no invented figures.
  Raw reseller names must not be included in external-facing text.

## Success and error stopping conditions

- **Success:** Return a valid JSON result with drafts held for approval,
  or correctly return zero drafts if no category crosses the
  threshold. Every drafted number is traceable.
- **Error:** If `validate_feed` returns False, Hard Stop immediately.
  Return its errors, with no MoM results or drafts. Never silently
  skip bad rows.

## Given–When–Then agent-level specifications

1. **GIVEN** April→May Ethnic Wear revenue moves from 104520.77 to
   185107.61, **WHEN** the agent evaluates the valid feed, **THEN**
   `mom_growth` returns 77.1 and `is_flagged` returns `"flagged"`;
   this category is eligible for a held draft.
2. **GIVEN** May→June Beauty & Personal Care revenue moves from
   35542.11 to 37559.07, **WHEN** the agent evaluates the valid feed,
   **THEN** `mom_growth` returns 5.67 and `is_flagged` returns
   `"not_flagged"`; no draft or suppression entry is made for it.
3. **GIVEN** a synthetic previous value of 100000 and current value
   of 108000, **WHEN** the agent evaluates the exact boundary,
   **THEN** `mom_growth` returns 8.0 and `is_flagged` returns
   `"escalate_exact_boundary"`; the category is escalated, not drafted.
4. **GIVEN** the specified corrupted feed, **WHEN** `validate_feed`
   runs, **THEN** it returns False with exactly three errors in order:
   the negative-revenue row, missing-category row and missing-revenue
   row; the agent Hard Stops without calculating MoM.

## Structured result

Every run returns exactly these top-level keys:

- `run_month`
- `validation_status`: `valid` or `invalid`
- `validation_errors`: list, empty on success
- `flagged_categories`: up to three objects, each with `category`,
  `mom_pct`, `previous_revenue`, `current_revenue`, `drafted`, and
  `message` when drafted
- `suppressed_categories`: names of flagged categories beyond the cap
- `escalated_categories`: names at the exact threshold boundary
- `action_taken`: `drafted_and_held_for_approval` or `hard_stop`

There is no network call, API key, or message-sending integration.
