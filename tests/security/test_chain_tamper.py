from __future__ import annotations

import unittest

from packages.evidence_store.chain import ChainBreak, chain_path, reset_store, verify_chain
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import batch_pack
from tests.helpers import load_pub


class ChainTamperTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_store()
        self._paths: list = []

    def tearDown(self) -> None:
        for path in self._paths:
            if path.exists():
                path.unlink()

    def test_altered_byte_names_the_first_broken_link(self) -> None:
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        path = chain_path(pack["request_id"])
        self._paths.append(path)
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("completed", "COMPROMISED", 1), encoding="utf-8")
        with self.assertRaises(ChainBreak) as ctx:
            verify_chain(pack["request_id"])
        self.assertIn("first broken link", str(ctx.exception))

    def test_deleted_middle_record_is_detected(self) -> None:
        pack = batch_pack(load_pub("PUB-02"), batch_id="NCS310-S26033")
        path = chain_path(pack["request_id"])
        self._paths.append(path)
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        del lines[2]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaises(ChainBreak) as ctx:
            verify_chain(pack["request_id"])
        self.assertIn("first broken link", str(ctx.exception))
