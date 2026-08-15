from __future__ import annotations

import os
import unittest

from packages.evidence_store.chain import ChainBreak, rebuild_index, reset_store, verify_chain
from packages.evidence_store.writer import persist_run
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack, batch_pack
from tests.helpers import load_pub


class EvidenceChainTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_store()

    def test_fixture_run_writes_request_inputs_pack_decisions_outcome(self) -> None:
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        rows = verify_chain(pack["request_id"])
        types = [row["type"] for row in rows]
        self.assertIn("request", types)
        self.assertIn("inputs", types)
        self.assertIn("pack", types)
        self.assertIn("decisions", types)
        self.assertIn("audit", types)
        self.assertEqual(types.count("outcome"), 1)
        self.assertEqual(sum(1 for row in rows if row["type"] == "request"), 1)
