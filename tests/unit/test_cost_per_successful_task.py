from __future__ import annotations

import unittest
from decimal import Decimal

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class CostPerSuccessfulTaskTests(unittest.TestCase):
    def test_denominator_is_successful_tasks(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-14"))
        rows = {item["workflow"]: item for item in pack["human_review"]["finops"]["workflows"]}
        self.assertEqual(rows["batch_review"]["successful_tasks"], "1110")
        self.assertEqual(rows["pv_intake"]["successful_tasks"], "2800")
        self.assertEqual(rows["batch_review"]["denominator"], "successful_tasks")
        per = Decimal(rows["batch_review"]["cost_per_successful_task"])
        inf = Decimal(rows["batch_review"]["inference_cost"])
        self.assertEqual(per, inf / Decimal("1110"))
        self.assertNotEqual(rows["batch_review"]["successful_tasks"], rows["batch_review"]["requests"])
