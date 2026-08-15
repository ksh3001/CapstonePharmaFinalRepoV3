from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class CostAbstentionTests(unittest.TestCase):
    def test_missing_minutes_abstain(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-14"))
        hits = [item for item in pack["abstentions"] if item.get("reason_code") == "human_review_duration_unavailable"]
        self.assertTrue(hits)
