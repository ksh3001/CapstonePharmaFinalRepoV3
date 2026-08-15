from __future__ import annotations

import unittest
from decimal import Decimal

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class InferenceCostTests(unittest.TestCase):
    def test_hand_recompute_matches_pack(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-14"))
        rows = {item["workflow"]: item for item in pack["human_review"]["finops"]["workflows"]}
        input_price = Decimal("8.50")
        output_price = Decimal("22.00")
        expected = (Decimal("5800000") / Decimal("1000000")) * input_price + (
            Decimal("850000") / Decimal("1000000")
        ) * output_price
        self.assertEqual(rows["batch_review"]["inference_cost"], format(expected, "f"))
