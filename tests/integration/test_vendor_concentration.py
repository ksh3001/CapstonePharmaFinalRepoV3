from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class VendorConcentrationTests(unittest.TestCase):
    def test_single_vendor_and_alternative_are_named(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-14"))
        conc = pack["human_review"]["finops"]["concentration"]
        self.assertTrue(conc["single_vendor"])
        self.assertEqual(conc["vendor"], "AIVENDOR-X")
        self.assertEqual(conc["alternative"], "LOCAL-SLM")
        self.assertTrue(conc["exit_cost"])
