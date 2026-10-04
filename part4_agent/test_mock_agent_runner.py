import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from part4_agent.mock_agent_runner import DEFAULT_FEED, run


CORRUPTED_FEED = "part2_engine/fixtures/corrupted_feed.csv"

EXPECTED_KEYS = {
    "run_month",
    "validation_status",
    "validation_errors",
    "flagged_categories",
    "suppressed_categories",
    "escalated_categories",
    "action_taken",
}


class MockAgentRunnerTests(unittest.TestCase):

    def test_may_run(self):
        result = run("May", str(DEFAULT_FEED), str(DEFAULT_FEED))

        self.assertEqual(set(result), EXPECTED_KEYS)
        self.assertEqual(result["validation_status"], "valid")
        self.assertEqual(result["validation_errors"], [])
        self.assertEqual(result["escalated_categories"], [])
        self.assertEqual(
            [x["category"] for x in result["flagged_categories"]],
            ["Ethnic Wear", "Western Wear", "Kids Wear"],
        )
        self.assertEqual(
            [x["mom_pct"] for x in result["flagged_categories"]],
            [77.1, -23.6, -23.48],
        )
        self.assertEqual(
            set(result["suppressed_categories"]),
            {"Beauty & Personal Care", "Home & Kitchen"},
        )

        for item in result["flagged_categories"]:
            self.assertTrue(item["drafted"])
            self.assertIn(item["category"], item["message"])
            self.assertIn(str(item["mom_pct"]), item["message"])

    def test_june_run(self):
        result = run("June", str(DEFAULT_FEED), str(DEFAULT_FEED))

        self.assertEqual(set(result), EXPECTED_KEYS)
        self.assertEqual(result["validation_status"], "valid")
        self.assertEqual(result["escalated_categories"], [])
        self.assertEqual(
            [x["category"] for x in result["flagged_categories"]],
            ["Ethnic Wear", "Home & Kitchen", "Kids Wear"],
        )
        self.assertEqual(
            [x["mom_pct"] for x in result["flagged_categories"]],
            [-58.74, 42.59, 23.9],
        )
        self.assertEqual(
            result["suppressed_categories"],
            ["Western Wear"],
        )
        self.assertNotIn(
            "Beauty & Personal Care",
            result["suppressed_categories"],
        )

    def test_corrupted_feed_hard_stops(self):
        result = run("May", str(DEFAULT_FEED), CORRUPTED_FEED)

        self.assertEqual(set(result), EXPECTED_KEYS)
        self.assertEqual(result["validation_status"], "invalid")
        self.assertEqual(result["action_taken"], "hard_stop")
        self.assertEqual(result["flagged_categories"], [])
        self.assertEqual(result["suppressed_categories"], [])
        self.assertEqual(result["escalated_categories"], [])
        self.assertEqual(
            result["validation_errors"],
            [
                "line 3: negative revenue (-4200.0) "
                "for category=Western Wear",
                "line 4: missing category (month=July)",
                "line 6: missing revenue (category=Home & Kitchen)",
            ],
        )


if __name__ == "__main__":
    unittest.main()
