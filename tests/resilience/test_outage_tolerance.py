from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class OutageToleranceTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_zero_hour_pv_intake_is_manual_immediately(self) -> None:
        pack = advisory_pack(load_pub("PUB-10"))
        workflows = {item["workflow"]: item for item in pack["human_review"]["continuity"]["workflows"]}
        pv = workflows["pv_intake"]
        self.assertTrue(pv["manual_immediately"])
        self.assertEqual(pv["path"], "manual")
        self.assertEqual(pv["max_ai_outage_hours"], "0")
        self.assertFalse(pv["continue_degraded"])
        rendered = str(pv).casefold()
        self.assertNotIn("grace", rendered)

    def test_fourteen_day_workflows_continue_degraded_with_deadline(self) -> None:
        pack = advisory_pack(load_pub("PUB-10"))
        workflows = {item["workflow"]: item for item in pack["human_review"]["continuity"]["workflows"]}
        for name in ("batch_review", "supply_planning"):
            row = workflows[name]
            self.assertTrue(row["continue_degraded"], name)
            self.assertEqual(row["degraded_deadline_days"], "14", name)
            self.assertEqual(row["path"], "degraded", name)
            self.assertFalse(row["manual_immediately"], name)
