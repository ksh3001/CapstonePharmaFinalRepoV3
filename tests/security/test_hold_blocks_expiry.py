from __future__ import annotations

import unittest

from packages.evidence_store.chain import load_chain
from packages.evidence_store.retention import maybe_expire_llm
from tests.helpers import fixture_with


class HoldBlocksExpiryTests(unittest.TestCase):
    def test_active_hold_blocks_expiry_and_records_refusal(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/legal_holds.csv",
                    "records": [{"hold_id": "LH-44", "scope": "NCB204-B24071", "status": "active"}],
                }
            ],
            scenario_id="HOLD-TTL",
            workflow="privacy",
        )
        result = maybe_expire_llm(
            "REQ-HOLD-TTL",
            recorded_at="2026-01-01T00:00:00+00:00",
            as_of="2026-08-01T08:00:00Z",
            record_type="llm",
            fixture=fixture,
        )
        self.assertFalse(result["expired"])
        self.assertEqual(result["reason"], "legal_hold")
        self.assertIn("LH-44", result["holds"])
        types = [row["type"] for row in load_chain("REQ-HOLD-TTL")]
        self.assertIn("hold_refusal", types)
        self.assertNotIn("expiry", types)
