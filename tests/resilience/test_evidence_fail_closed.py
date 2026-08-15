from __future__ import annotations

import os
import unittest

from packages.evidence_store.chain import StoreUnwritable, reset_store
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import batch_pack
from tests.helpers import load_pub


class EvidenceFailClosedTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_store()

    def test_read_only_store_emits_no_pack(self) -> None:
        old = os.environ.get("AEGIS_EVIDENCE_READONLY")
        os.environ["AEGIS_EVIDENCE_READONLY"] = "1"
        try:
            with self.assertRaises(StoreUnwritable):
                batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        finally:
            if old is None:
                os.environ.pop("AEGIS_EVIDENCE_READONLY", None)
            else:
                os.environ["AEGIS_EVIDENCE_READONLY"] = old
