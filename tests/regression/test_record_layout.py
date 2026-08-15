from __future__ import annotations

import unittest

from packages.evidence_store.chain import load_chain, reset_store
from packages.kernel.canonical import dumps
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class RecordLayoutTests(unittest.TestCase):
    def test_layout_keys_are_stable(self) -> None:
        reset_replay()
        reset_store()
        pack = advisory_pack(load_pub("PUB-13"))
        rows = load_chain(pack["request_id"])
        for row in rows:
            self.assertIn("seq", row)
            self.assertIn("type", row)
            self.assertIn("prev_hash", row)
            self.assertIn("entry_hash", row)
            self.assertIn("payload", row)
        self.assertEqual(dumps(rows[0])[-1:], b"\n")
