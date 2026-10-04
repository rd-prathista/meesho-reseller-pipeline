import unittest
from pathlib import Path

from part3_narrative.masking import (
    alias_for,
    assert_no_raw_names_leak,
)


REPORT_PATH = Path(__file__).resolve().parent / "narrative_report.md"


class MaskingTests(unittest.TestCase):

    def test_alias_examples(self):
        self.assertEqual(alias_for("RS019"), "ALIAS-19")
        self.assertEqual(alias_for("RS006"), "ALIAS-06")

    def test_final_top_reseller_narrative_has_no_raw_names(self):
        report = REPORT_PATH.read_text(encoding="utf-8")

        # Read the report's actual top-reseller section, not a
        # separate example that could differ from the final narrative.
        narrative = report.split(
            "## Top-reseller narrative for internal review", 1
        )[1]

        raw_names = [
            "Mumbai Reseller 1",
            "Mumbai Reseller 4",
            "Hyderabad Reseller 6",
            "Lucknow Reseller 6",
            "Jaipur Reseller 5",
        ]

        self.assertIn("ALIAS-19", narrative)
        self.assertTrue(
            assert_no_raw_names_leak(narrative, raw_names)
        )

    def test_raw_name_is_rejected(self):
        bad_narrative = (
            "West-region Mumbai Reseller 1 has high spend."
        )

        self.assertFalse(
            assert_no_raw_names_leak(
                bad_narrative, ["Mumbai Reseller 1"]
            )
        )


if __name__ == "__main__":
    unittest.main()
