# Reseller growth narrative report

All measured figures below come from the seeded Part 1 SQL output.
Month-on-month percentages come from Part 2's `mom_growth` function.
A suggested explanation is not treated as an established fact.

## Worked narrative: May Ethnic Wear

**Context:** Ethnic Wear category revenue is being compared for May
against April 2026.

**Insight — FACT:** Ethnic Wear revenue increased from INR 104520.77
in April to INR 185107.61 in May. The month-on-month change was
+77.1%, which Part 2 flagged.

**Implication — RECOMMENDATION:** Ask the category manager to compare
April and May Ethnic Wear order counts and check whether the increase
is spread across resellers or concentrated among a small number of
them. **HYPOTHESIS:** A change in order volume or reseller
concentration may help explain the movement; this revenue comparison
alone does not establish its cause.

## Worked narrative: June Ethnic Wear

**Context:** Ethnic Wear category revenue is being compared for June
against May 2026.

**Insight — FACT:** Ethnic Wear revenue decreased from INR 185107.61
in May to INR 76371.53 in June. The month-on-month change was
-58.74%, which Part 2 flagged.

**Implication — RECOMMENDATION:** Ask the category manager to compare
May and June Ethnic Wear order counts and inspect whether the
decline is concentrated among particular resellers before deciding
on an intervention. **HYPOTHESIS:** A change in order volume or
reseller activity may be involved; revenue totals alone cannot
prove the cause.

## Self-score against the refinement checklist

- **Specificity — passes:** Both blocks identify Ethnic Wear,
  the correct pair of months, the verified revenues, and the exact
  Part 2 percentage.
- **Audience fit — passes:** A regional manager can read the result
  and next action without needing to understand SQL or Python.
- **Completeness — passes:** Each block separately states Context,
  Insight, and Implication.
- **Actionability — passes:** Each recommendation says what to
  compare next rather than merely saying to investigate the category.

## Chart-choice justification

### Which month had the highest total revenue?

Use a simple **vertical bar chart** with April (INR 419417.43), May
(INR 444594.25), and June (INR 398055.24) as the three bars; May is
highest. This is a **bivariate** comparison of month and total
revenue. Label the values so the answer is clear within 10 seconds,
start the revenue y-axis at zero, avoid 3D, and omit a legend because
there is only one series.

### What share of April revenue came from Ethnic Wear?

Use a **100% stacked bar** showing Ethnic Wear's INR 104520.77
against the remainder of April's INR 419417.43 total; label the
Ethnic Wear segment **24.92%**. This is a **bivariate part-to-whole**
view: category grouping and share of one month's total. The
percentage label makes the answer clear within 10 seconds. The bar
starts at zero; avoid 3D. Label the segments directly rather than
adding an unnecessary legend.

### How do the four regions compare on total revenue?

Use a **horizontal bar chart** with North (INR 337125.46), West
(INR 333106.33), South (INR 316736.68), and East
(INR 275098.45), sorted from highest to lowest. This is a
**bivariate** comparison of region and revenue. Direct labels make
the ranking clear within 10 seconds; start the revenue axis at zero,
avoid 3D, and omit a legend because there is only one series.

## Top-reseller narrative for internal review

**FACT:** In the seeded all-order spend query, West-region reseller
ALIAS-19 has total spend of INR 75295.09. **RECOMMENDATION:** Ask the
regional manager to verify whether this spend is spread across
categories before using it to plan reseller support. This paragraph
uses a coded alias rather than a raw reseller name.
