from __future__ import annotations

import json
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class NoEstimatedCostTests(unittest.TestCase):
    def test_pack_does_not_claim_an_estimate(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-14"))
        self.assertFalse(pack["human_review"]["finops"]["estimated"])
        rendered = json.dumps(pack).casefold()
        self.assertNotIn("estimated cost", rendered)
        self.assertNotIn("interpolated", rendered)
        self.assertNotIn("assumed cost", rendered)
