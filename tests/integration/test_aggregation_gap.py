from __future__ import annotations

import unittest

from packages.kernel.packs import supply_pack
from tests.helpers import fixture_with


class AggregationGapTests(unittest.TestCase):
    def test_missing_pallet_is_a_gap_and_parent_is_not_inferred(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/serialisation_events.csv",
                    "records": [
                        {
                            "serial": "SN-10001",
                            "event": "commission",
                            "case": "CS-77",
                            "pallet": "P-88",
                        },
                        {
                            "serial": "SN-10002",
                            "event": "commission",
                            "case": "CS-77",
                            "pallet": "",
                        },
                    ],
                }
            ],
            scenario_id="SYN-AGG",
            workflow="supply",
        )
        pack = supply_pack(fixture, event_id="SN-10002")
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "aggregation_gap"]
        self.assertTrue(gaps)
        gap = gaps[0]
        self.assertEqual(gap["subject_id"], "SN-10002")
        self.assertEqual(gap["expected_parent"], "pallet")
        self.assertIn("CS-77", str(gap.get("case") or gap.get("statement") or ""))
        rendered = str(pack)
        self.assertNotIn("inferred_parent", rendered)
        self.assertNotIn("P-88", str(gap))
        self.assertNotIn("aggregation_complete", rendered)
