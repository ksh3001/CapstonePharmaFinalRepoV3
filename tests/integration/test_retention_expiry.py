from __future__ import annotations

import unittest

from packages.evidence_store.chain import load_chain
from packages.evidence_store.retention import maybe_expire_llm
from tests.helpers import fixture_with


def _hold_fixture(status: str = "active") -> dict:
    return fixture_with(
        [
            {
                "source": "data/legal_holds.csv",
                "records": [{"hold_id": "LH-44", "scope": "NCB204-B24071", "status": status}],
            }
        ],
        scenario_id="RETENTION",
        workflow="privacy",
    )


class RetentionExpiryTests(unittest.TestCase):
    def test_llm_logs_expire_after_ninety_days_as_an_event(self) -> None:
        fixture = fixture_with([], scenario_id="TTL", workflow="privacy")
        result = maybe_expire_llm(
            "REQ-TTL",
            recorded_at="2026-01-01T00:00:00+00:00",
            as_of="2026-08-01T08:00:00Z",
            record_type="llm",
            fixture=fixture,
        )
        self.assertTrue(result["expired"])
        self.assertEqual(result["reason"], "ttl")
        types = [row["type"] for row in load_chain("REQ-TTL")]
        self.assertIn("expiry", types)

    def test_clinical_and_icsr_records_never_expire(self) -> None:
        fixture = fixture_with([], scenario_id="CLIN", workflow="clinical")
        for record_type in ("clinical", "ICSR", "icsr", "clinical_trial_source"):
            result = maybe_expire_llm(
                "REQ-CLIN",
                recorded_at="2020-01-01T00:00:00+00:00",
                as_of="2026-08-01T08:00:00Z",
                record_type=record_type,
                fixture=fixture,
            )
            self.assertFalse(result["expired"])
            self.assertEqual(result["reason"], "clinical_or_icsr_retained")
        types = [row["type"] for row in load_chain("REQ-CLIN")]
        self.assertNotIn("expiry", types)
