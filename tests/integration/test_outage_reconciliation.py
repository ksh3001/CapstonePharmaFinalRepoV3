from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class OutageReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_resumption_without_reconciliation_is_blocked(self) -> None:
        fixture = load_pub("PUB-10")
        fixture["authorized_context"]["resume_ai"] = True
        pack = advisory_pack(fixture)
        blocked = [
            item
            for item in pack["abstentions"]
            if item.get("reason_code") == "outage_reconciliation_required"
        ]
        self.assertTrue(blocked)
        self.assertTrue(pack["human_review"]["continuity"]["resumption_requires_reconciliation"])

    def test_reconciled_outage_does_not_emit_the_block(self) -> None:
        fixture = load_pub("PUB-10")
        fixture["authorized_context"]["resume_ai"] = True
        fixture["authorized_context"]["outage_reconciled"] = True
        pack = advisory_pack(fixture)
        blocked = [
            item
            for item in pack["abstentions"]
            if item.get("reason_code") == "outage_reconciliation_required"
        ]
        self.assertFalse(blocked)
