from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class MissingCostIsGapTests(unittest.TestCase):
    def test_zero_review_costs_are_missing(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-14"))
        missing = pack["human_review"]["finops"]["missing_components"]
        self.assertIn("human_quality_review", missing)
        self.assertIn("medical_review", missing)
        self.assertFalse(pack["human_review"]["finops"]["total_complete"])
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "missing_cost"]
        self.assertTrue(gaps)
