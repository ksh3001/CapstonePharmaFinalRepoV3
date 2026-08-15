from __future__ import annotations

import unittest

from packages.evidence_store.chain import load_chain, rebuild_index, reset_store, verify_chain
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import batch_pack
from tests.helpers import load_pub


class EvidenceRetrievalTests(unittest.TestCase):
    def test_chain_is_complete_for_request_id(self) -> None:
        reset_replay()
        reset_store()
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        rows = load_chain(pack["request_id"])
        self.assertGreaterEqual(len(rows), 5)
        verify_chain(pack["request_id"])
        index = rebuild_index()
        self.assertTrue(any(item["request_id"] == pack["request_id"] for item in index["chains"]))
