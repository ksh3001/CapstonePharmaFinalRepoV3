from __future__ import annotations

import unittest

from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class PendingAmendmentTests(unittest.TestCase):
    def test_pending_is_neither_approved_nor_rejected(self) -> None:
        pack = advisory_pack(load_pub("PUB-15"))
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "pending_amendment"]
        self.assertTrue(gaps)
        statement = gaps[0]["statement"].casefold()
        self.assertIn("pending", statement)
        self.assertIn("neither approved nor rejected", statement)
        self.assertNotIn("5.0 applies", statement)
