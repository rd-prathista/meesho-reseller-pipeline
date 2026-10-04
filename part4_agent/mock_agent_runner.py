import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from part2_engine.growth_engine import (
    is_flagged,
    mom_growth,
    validate_feed,
)
from part3_narrative.template_fill import draft_flagged_category


DEFAULT_FEED = (
    PROJECT_ROOT / "part1_sql" / "output" / "monthly_category_revenue.csv"
)


def make_result(month: str) -> dict:
    """Create every required top-level JSON key."""
    return {
        "run_month": month,
        "validation_status": "valid",
        "validation_errors": [],
        "flagged_categories": [],
        "suppressed_categories": [],
        "escalated_categories": [],
        "action_taken": "drafted_and_held_for_approval",
    }


def hard_stop(result: dict, errors: list[str]) -> dict:
    """Return an invalid result without any computed categories."""
    result["validation_status"] = "invalid"
    result["validation_errors"] = errors
    result["action_taken"] = "hard_stop"
    return result


def load_month(csv_path: str, month: str) -> dict[str, float]:
    """Get category -> revenue for one month from a validated feed."""
    revenues = {}

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            if row["month"].strip() == month:
                category = row["category"].strip()

                if category in revenues:
                    raise ValueError(
                        f"duplicate category={category} for month={month}"
                    )

                revenues[category] = float(row["revenue"])

    if not revenues:
        raise ValueError(f"month={month} not found in feed")

    return revenues


def run(
    month: str,
    previous_month_csv: str,
    current_month_csv: str,
) -> dict:
    """Validate, compare, classify and hold up to three offline drafts.

    previous_month_csv and current_month_csv may both point to the
    Part 1 15-row CSV. The requested months are selected from its rows.
    """
    result = make_result(month)

    # Step 1 and 2: validate current input FIRST. A corrupted current
    # feed must Hard Stop before any MoM calculation is attempted.
    valid, errors = validate_feed(current_month_csv)
    if not valid:
        return hard_stop(result, errors)

    # Validate the comparison feed before using it as well.
    previous_valid, previous_errors = validate_feed(previous_month_csv)
    if not previous_valid:
        return hard_stop(result, previous_errors)

    previous_month_by_current = {
        "May": "April",
        "June": "May",
    }

    if month not in previous_month_by_current:
        return hard_stop(
            result,
            [f"unsupported run month: {month!r}; use May or June"],
        )

    prev_month = previous_month_by_current[month]

    try:
        previous = load_month(previous_month_csv, prev_month)
        current = load_month(current_month_csv, month)

        if set(previous) != set(current):
            raise ValueError(
                "previous and current months have different categories"
            )

        flagged = []

        # Steps 3, 4 and 7b: use the Part 2 functions unmodified.
        for category, current_revenue in current.items():
            previous_revenue = previous[category]
            growth = mom_growth(previous_revenue, current_revenue)
            decision = is_flagged(growth)

            if decision == "escalate_exact_boundary":
                result["escalated_categories"].append(category)

            elif decision == "flagged":
                flagged.append(
                    {
                        "category": category,
                        "mom_pct": growth,
                        "previous_revenue": previous_revenue,
                        "current_revenue": current_revenue,
                    }
                )

            # "not_flagged" categories need no message or suppression.

        # Steps 5, 6 and 7: magnitude order, with a three-draft cap.
        flagged.sort(
            key=lambda item: abs(item["mom_pct"]),
            reverse=True,
        )

        for item in flagged[:3]:
            item["drafted"] = True
            item["message"] = draft_flagged_category(
                category=item["category"],
                prev_month=prev_month,
                month=month,
                previous_revenue=item["previous_revenue"],
                current_revenue=item["current_revenue"],
                mom_pct=item["mom_pct"],
            )
            result["flagged_categories"].append(item)

        result["suppressed_categories"] = [
            item["category"] for item in flagged[3:]
        ]

    except ValueError as error:
        # Missing comparison data and undefined growth are not silently
        # ignored; return a clean Hard Stop instead.
        return hard_stop(make_result(month), [str(error)])

    # Step 8: return one structured object. The CLI prints it as JSON.
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Offline Meesho category growth agent"
    )
    parser.add_argument(
        "month",
        choices=["May", "June"],
        help="Current month to evaluate",
    )
    parser.add_argument(
        "--previous-csv",
        default=str(DEFAULT_FEED),
        help="CSV containing the previous month's rows",
    )
    parser.add_argument(
        "--current-csv",
        default=str(DEFAULT_FEED),
        help="CSV containing the current month's rows",
    )
    args = parser.parse_args()

    output = run(
        args.month,
        args.previous_csv,
        args.current_csv,
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
