from __future__ import annotations

import unittest

from packages.kernel.packs import supply_pack
from tests.helpers import load_pub


class QualityHoldsTests(unittest.TestCase):
    def test_global_quarantine_is_on_every_affected_option(self) -> None:
        pack = supply_pack(load_pub("PUB-07"), event_id="NCB-204-shortage")
        holds = pack["quality_holds"]
        self.assertTrue(holds)
        self.assertTrue(
            any(
                str(item.get("units")) == "5100" and str(item.get("quality_status")).casefold() == "quarantine"
                for item in holds
            ),
            holds,
        )
        hold_ids = {str(item.get("hold_id")) for item in holds}
        for option in pack["options"]:
            if option.get("product") == "NCB-204" or option.get("channel"):
                attached = set(option.get("quality_holds") or [])
                self.assertTrue(hold_ids & attached, option.get("option_id"))
                for position in option.get("released_positions") or []:
                    self.assertNotEqual(str(position.get("units")), "5100")
                    self.assertNotEqual(str(position.get("market")), "Global")
