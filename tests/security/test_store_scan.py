from __future__ import annotations

import unittest

from packages.evidence_store.chain import load_chain, reset_store, verify_chain
from packages.evidence_store.scan import scan_store
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import batch_pack
from tests.helpers import load_pub


class StoreScanTests(unittest.TestCase):
    def test_persisted_chain_has_no_secrets_or_direct_ids(self) -> None:
        reset_replay()
        reset_store()
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        rows = load_chain(pack["request_id"])
        self.assertEqual(scan_store(rows), [])
        verify_chain(pack["request_id"])
