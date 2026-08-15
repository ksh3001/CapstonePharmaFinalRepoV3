from __future__ import annotations

import unittest

from packages.kernel.packs import supply_pack
from tests.helpers import load_pub


class SupplyOptionsTests(unittest.TestCase):
    def test_approvals_required_where_stock_would_move(self) -> None:
        pack = supply_pack(load_pub("PUB-07"), event_id="NCB-204-shortage")
        self.assertTrue(pack["approvals_required"])
        self.assertTrue(pack["options"])
        for option in pack["options"]:
            if option.get("channel"):
                self.assertTrue(
                    option.get("approvals_required"),
                    option.get("option_id"),
                )
        rendered = str(pack)
        self.assertNotIn("ranking_score", rendered)
        self.assertNotIn("priority_score", rendered)
        compassionate = [item for item in pack["options"] if "compassionate" in str(item.get("channel") or "")]
        self.assertTrue(compassionate)
        self.assertIn("ethics_board", compassionate[0]["approvals_required"])
