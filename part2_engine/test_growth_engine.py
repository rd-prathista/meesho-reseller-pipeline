import csv
import unittest
from pathlib import Path

from part2_engine.growth_engine import (
    is_flagged,
    mom_growth,
    validate_feed,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MONTHLY_CSV = (
    PROJECT_ROOT / "part1_sql" / "output" / "monthly_category_revenue.csv"
)
CORRUPTED_CSV = (
    PROJECT_ROOT / "part2_engine" / "fixtures" / "corrupted_feed.csv"
)


def load_monthly_revenues():
    """Turn the Part 1 CSV into a month/category lookup for the tests."""
    revenues = {}

    with MONTHLY_CSV.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            revenues[(row["month"], row["category"])] = float(row["revenue"])

    return revenues


class GrowthEngineTests(unittest.TestCase):

    def test_given_april_to_may_ethnic_when_evaluated_then_flagged(self):
        # GIVEN April and May Ethnic Wear revenue
        # WHEN growth and flagging are calculated
        result = mom_growth(104520.77, 185107.61)

        # THEN growth is 77.1% and it is flagged
        self.assertEqual(result, 77.1)
        self.assertEqual(is_flagged(result), "flagged")

    def test_given_may_to_june_beauty_when_evaluated_then_not_flagged(self):
        # GIVEN May and June Beauty & Personal Care revenue
        # WHEN growth and flagging are calculated
        result = mom_growth(35542.11, 37559.07)

        # THEN growth is 5.67% and it is not flagged
        self.assertEqual(result, 5.67)
        self.assertEqual(is_flagged(result), "not_flagged")

    def test_given_exact_eight_percent_when_evaluated_then_escalated(self):
        # GIVEN values chosen to create exactly 8.0% growth
        # WHEN growth and flagging are calculated
        result = mom_growth(100000, 108000)

        # THEN neither automatic outcome is selected
        self.assertEqual(result, 8.0)
        self.assertEqual(is_flagged(result), "escalate_exact_boundary")

    def test_given_corrupted_feed_when_validated_then_three_errors(self):
        # GIVEN a file with negative, missing-category and missing-revenue rows
        # WHEN validation runs
        valid, errors = validate_feed(str(CORRUPTED_CSV))

        # THEN it fails with exactly these errors in row order
        self.assertFalse(valid)
        self.assertEqual(
            errors,
            [
                "line 3: negative revenue (-4200.0) "
                "for category=Western Wear",
                "line 4: missing category (month=July)",
                "line 6: missing revenue (category=Home & Kitchen)",
            ],
        )

    def test_given_real_part1_feed_when_validated_then_no_errors(self):
        # GIVEN Part 1's actual 15-row output
        # WHEN validation runs
        valid, errors = validate_feed(str(MONTHLY_CSV))

        # THEN the entire file passes
        self.assertEqual((valid, errors), (True, []))

        with MONTHLY_CSV.open(newline="", encoding="utf-8") as file:
            self.assertEqual(len(list(csv.DictReader(file))), 15)

    def test_given_all_april_may_categories_when_evaluated_then_expected(self):
        # GIVEN every category in Part 1's April and May output
        revenues = load_monthly_revenues()
        expected = {
            "Ethnic Wear": (77.1, "flagged"),
            "Western Wear": (-23.6, "flagged"),
            "Kids Wear": (-23.48, "flagged"),
            "Home & Kitchen": (-9.25, "flagged"),
            "Beauty & Personal Care": (-12.75, "flagged"),
        }

        # WHEN each category is evaluated
        # THEN all five match the specified growth and flag result
        for category, (expected_growth, expected_flag) in expected.items():
            with self.subTest(category=category):
                growth = mom_growth(
                    revenues[("April", category)],
                    revenues[("May", category)],
                )
                self.assertEqual(growth, expected_growth)
                self.assertEqual(is_flagged(growth), expected_flag)

    def test_given_all_may_june_categories_when_evaluated_then_expected(self):
        # GIVEN every category in Part 1's May and June output
        revenues = load_monthly_revenues()
        expected = {
            "Ethnic Wear": (-58.74, "flagged"),
            "Western Wear": (11.97, "flagged"),
            "Kids Wear": (23.9, "flagged"),
            "Home & Kitchen": (42.59, "flagged"),
            "Beauty & Personal Care": (5.67, "not_flagged"),
        }

        # WHEN each category is evaluated
        # THEN four are flagged; Beauty & Personal Care is not
        for category, (expected_growth, expected_flag) in expected.items():
            with self.subTest(category=category):
                growth = mom_growth(
                    revenues[("May", category)],
                    revenues[("June", category)],
                )
                self.assertEqual(growth, expected_growth)
                self.assertEqual(is_flagged(growth), expected_flag)


if __name__ == "__main__":
    unittest.main()
