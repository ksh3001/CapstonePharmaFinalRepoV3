from __future__ import annotations

import json
import unittest

from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class DsrVsHoldTests(unittest.TestCase):
    def test_dsr17_against_lh44_is_restriction_not_deletion(self) -> None:
        pack = advisory_pack(load_pub("PUB-11"))
        self.assertEqual(pack["authorization"]["decision"], "allow")
        statements = " ".join(item.get("statement") or "" for item in pack["findings"])
        self.assertIn("DSR-17", statements)
        self.assertIn("LH-44", statements)
        self.assertIn("restriction", statements.casefold())
        self.assertIn("retained", statements.casefold())
        rendered = json.dumps(pack).casefold()
        self.assertNotIn("was deleted", rendered)
        self.assertNotIn("will be deleted", rendered)
        self.assertNotIn("data deleted", rendered)
        self.assertTrue(pack["no_side_effects"])
