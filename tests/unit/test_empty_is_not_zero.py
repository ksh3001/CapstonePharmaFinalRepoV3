from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class EmptyIsNotZeroTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_empty_tolerance_is_not_specified(self) -> None:
        pack = advisory_pack(load_pub("PUB-10"))
        workflows = {item["workflow"]: item for item in pack["human_review"]["continuity"]["workflows"]}
        self.assertFalse(workflows["pv_intake"]["days_specified"])
        self.assertIsNone(workflows["pv_intake"]["max_ai_outage_days"])
        self.assertFalse(workflows["batch_review"]["hours_specified"])
        self.assertIsNone(workflows["batch_review"]["max_ai_outage_hours"])
        self.assertFalse(workflows["supply_planning"]["hours_specified"])
        self.assertIsNone(workflows["supply_planning"]["max_ai_outage_hours"])
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "tolerance_not_specified"]
        self.assertTrue(gaps)
        for gap in gaps:
            statement = str(gap.get("statement") or "").casefold()
            self.assertIn("not specified", statement)
            self.assertNotIn("unlimited", statement.split("not specified")[0])
            self.assertNotEqual(gap.get("max_ai_outage_hours"), 0)
            self.assertNotEqual(gap.get("max_ai_outage_days"), 0)
