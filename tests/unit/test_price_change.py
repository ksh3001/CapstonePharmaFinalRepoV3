from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class PriceChangeTests(unittest.TestCase):
    def test_both_prices_are_reported(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-14"))
        change = pack["human_review"]["finops"]["price_change"]
        self.assertEqual(change["previous"], "5.00")
        self.assertEqual(change["current"], "8.50")
        self.assertTrue(change["historical_not_restated"])
