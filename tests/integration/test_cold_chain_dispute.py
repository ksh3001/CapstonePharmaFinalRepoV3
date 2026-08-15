from __future__ import annotations

import unittest

from packages.kernel.packs import supply_pack
from tests.helpers import load_pub


class ColdChainDisputeTests(unittest.TestCase):
    def test_logger_pallet_dispute_retains_both_readings(self) -> None:
        pack = supply_pack(load_pub("PUB-08"), event_id="SH-901")
        cold = [item for item in pack["contradictions"] if item.get("topic") == "cold_chain"]
        self.assertTrue(cold)
        values = {str(value) for item in cold for value in item.get("values") or []}
        pallets = {str(value) for item in cold for value in item.get("pallets") or []}
        self.assertEqual(values, {"9.7", "10.8"})
        self.assertEqual(pallets, {"P-88", "P-89"})
        rendered = str(pack).casefold()
        self.assertNotIn("excursion confirmed", rendered)
        self.assertNotIn("excursion_verdict", rendered)
        self.assertNotIn("out of spec", rendered)
