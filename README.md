# Meesho Reseller Growth & Alert Intelligence Pipeline

A reproducible, offline reseller-growth monitoring pipeline. It
generates a seeded reseller/order dataset, computes business metrics
using SQLite, validates a monthly revenue feed, identifies significant
month-on-month category changes, and creates stakeholder-ready drafts
held for human approval.

**No API key, paid service, hosted runtime, or real AI API is needed.**
Narrative drafting uses a deterministic Python template. The runner
does not send email or messages.

## Requirements

- Python 3 with the standard library; tested locally with Python 3.14.8.
- Run the commands below from the project root (the folder containing
  this README). On Windows, use `py`. On a computer where `python` is
  the available command, replace `py` with `python`.
- No `pip install` step is required.

## Run the complete pipeline in order

### 1. Regenerate the dataset

```powershell
py data\generate_dataset.py
```

This runs the assignment's fixed, seeded script without changing its
seed, weights, or row counts. It writes:

- `data/resellers.csv` — 24 resellers
- `data/orders.csv` — 900 orders
- `data/meesho_reseller.db` — SQLite database containing both tables

The expected zero-order reseller is `RS024`. Regenerating the dataset
replaces the existing generated database.

### 2. Run Part 1: SQL business queries

```powershell
py part1_sql\queries.py
```

The SQL queries are in `part1_sql/queries.py`, using Python's
`sqlite3` module. Results are exported to `part1_sql/output/`.

The required hand-off file is
`part1_sql/output/monthly_category_revenue.csv`, with columns
`month,category,revenue,n_orders` and 15 data rows. The other CSVs
cover regions, top resellers, zero-order resellers, the LEFT JOIN
count demonstration, and June Delivered average order value.

Expected checks: grand total revenue is INR 1262066.92; June
Delivered AOV is INR 1267.69; for `RS024`, `COUNT(*) = 1` while
`COUNT(order_id) = 0`. See `part1_sql/output/README.md` for why
`COUNT(*)` cannot detect an unmatched LEFT JOIN row.

### 3. Run Part 2: feed validation and growth tests

```powershell
py -m unittest discover -s part2_engine -p "test_*.py" -v
```

`part2_engine/growth_engine.py` provides `validate_feed`,
`mom_growth`, and `is_flagged`. The tests read Part 1's monthly CSV
directly; no duplicate copy of that file is needed in `fixtures/`.
`fixtures/corrupted_feed.csv` verifies the three specified validation
errors.

A change with absolute magnitude above 8% is flagged; below 8% it
is not flagged; exactly 8% is escalated for human review. A previous
revenue of zero raises `ValueError`, because percentage growth from
zero is undefined.

### 4. Run Part 3: narrative and masking tests

```powershell
py -m unittest discover -s part3_narrative -p "test_*.py" -v
```

`prompt_pack.md` documents the trigger, inputs, narrative prompt and
validation checklist. `narrative_report.md` contains the worked May
and June narratives, written chart choices, self-score and masked
top-reseller narrative. `masking.py` checks aliases and raw-name
leaks. `template_fill.py` constructs offline, deterministic drafts
using the verified inputs; it never contacts an AI service.

### 5. Run Part 4: mock monitoring agent

```powershell
py -m unittest discover -s part4_agent -p "test_*.py" -v
py -m part4_agent.mock_agent_runner May
py -m part4_agent.mock_agent_runner June
py -m part4_agent.mock_agent_runner May --current-csv part2_engine\fixtures\corrupted_feed.csv
```

Each runner command prints one structured JSON object. The first
two commands use the 15-row Part 1 CSV as both input paths and select
April/May or May/June rows as appropriate. The last command uses the
deliberately corrupted CSV as the current feed and must Hard Stop.

Expected results:

- **May:** draft and hold Ethnic Wear, Western Wear, and Kids Wear;
  suppress Beauty & Personal Care and Home & Kitchen.
- **June:** draft and hold Ethnic Wear, Home & Kitchen, and Kids Wear;
  suppress Western Wear. Beauty & Personal Care is not flagged.
- **Corrupted feed:** `validation_status` is `invalid`,
  `action_taken` is `hard_stop`, there are three validation errors,
  and there are no drafts.
- `escalated_categories` is empty in these three dataset scenarios;
  an exact 8% synthetic case is tested in Part 2.

Nothing is automatically sent. Human approval is required before any
draft could be distributed.

## How the four Parts connect

1. **Part 1 → Part 2:** Compute real revenue and order numbers with
   SQL first, then hand the `month,category,revenue,n_orders` CSV to
   the validator and growth engine. Narrative text never substitutes
   for a database calculation.
2. **Part 2 → Part 3:** Only validated values and calculated
   month-on-month percentages are supplied to the offline narrative
   template. Facts are distinguished from hypotheses.
3. **Parts 1–3 → Part 4:** The runner follows an
   **Intake → Validate → Compare → Prioritise → Report Draft →
   Human Review** flow. Bad input causes a Hard Stop, at most three
   flagged categories receive held drafts, and other flagged
   categories are logged for manual review.

## Privacy and review guardrails

The top-reseller narrative uses a coded alias rather than a raw
reseller name. The masking test checks the final written narrative
and proves that a negative example containing a raw name fails.
Every numeric figure in an agent draft comes from the Part 1 feed
or Part 2 calculation. The runner makes no network calls.

## Python documentation

The implementation uses Python standard-library modules including
`csv`, `sqlite3`, `json`, `pathlib`, `argparse`, and `unittest`.
If official Python documentation was consulted during implementation,
list the specific pages consulted here before submission. Do not
claim to have consulted a page that you did not actually use.
