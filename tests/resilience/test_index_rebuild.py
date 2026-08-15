from __future__ import annotations

import unittest

from packages.evidence_store.chain import rebuild_index, reset_store
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import batch_pack
from tests.helpers import load_pub


class IndexRebuildTests(unittest.TestCase):
    def test_rebuilt_index_matches_second_build(self) -> None:
        reset_replay()
        reset_store()
        batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        first = rebuild_index()
        second = rebuild_index()
        self.assertEqual(first, second)
