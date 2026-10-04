# Reusable flagged-category prompt pack

## Trigger

Use this prompt only when Part 2's `is_flagged(mom_pct)` returns
`"flagged"` for a category. A `"not_flagged"` category receives no
draft. An `"escalate_exact_boundary"` category is held for separate
human review and receives no automatic draft.

## Input list

All values must come from the validated Part 1 monthly revenue CSV
or Part 2's calculation:

- `{category}`: category name
- `{prev_month}`: previous month name
- `{month}`: current month name
- `{previous_revenue}`: previous month's category revenue in INR
- `{current_revenue}`: current month's category revenue in INR
- `{mom_pct}`: Part 2's rounded month-on-month percentage

## Prompt

Write a short update for a regional manager about
`{category}` in `{month}` vs. `{prev_month}`.

Use the headings Context, Insight, and Implication.

Context: identify the category and the two months being compared.
Insight: explicitly label as FACT that revenue changed from
INR `{previous_revenue}` to INR `{current_revenue}`, a
`{mom_pct}`% month-on-month change.
Implication: recommend a specific next check. Label a proposed
explanation as HYPOTHESIS, not as a proven cause.

Never state a numeric figure unless it exactly matches one of the
supplied numeric placeholders. Do not invent causes, reseller names,
targets, order counts, or regional figures. If referencing a reseller,
use a coded alias rather than the raw reseller name. Draft for human
approval; do not send automatically.

## Checklist

Before using a draft, check all of the following:

1. The category and both month names match the supplied inputs exactly.
2. Every numeric figure in the draft is one of the supplied revenue
   values or the supplied `mom_pct`; there are no invented figures.
3. The draft has Context, Insight, and Implication sections.
4. The measured change is labeled FACT; any proposed cause is labeled
   HYPOTHESIS rather than asserted as fact.
5. The recommendation names a concrete next check or action.
6. No raw reseller name appears; any reseller reference uses a coded
   alias. The draft is held for human approval, not sent.
