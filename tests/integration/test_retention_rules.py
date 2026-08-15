from __future__ import annotations

import json
import unittest

from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class RetentionRuleTests(unittest.TestCase):
    def test_prompt_log_expiry_is_not_applied_under_hold(self) -> None:
        pack = advisory_pack(load_pub("PUB-11"))
        retention = [item for item in pack["findings"] if item.get("finding_id") == "F-RETENTION-HOLD"]
        self.assertTrue(retention, pack["findings"])
        statement = retention[0]["statement"].casefold()
        self.assertIn("90-day", statement)
        self.assertIn("lh-44", statement)
        self.assertIn("not applied", statement)
        self.assertTrue(pack.get("human_review", {}).get("hold_check", {}).get("checked"))
        self.assertIn("LH-44", pack["human_review"]["hold_check"]["active_holds"])
        self.assertNotIn("was deleted", json.dumps(pack).casefold())
