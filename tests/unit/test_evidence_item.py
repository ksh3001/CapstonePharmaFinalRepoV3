from __future__ import annotations

import unittest

from packages.domain.evidence import EvidenceItem, build_evidence_item
from packages.domain.types import Abstention
from scripts.build_fixture_copyset import build


class EvidenceItemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        build()

    def test_builder_uses_published_hash_and_as_of(self) -> None:
        item = build_evidence_item(
            source="data/batches.csv",
            record_id="NCB204-B24071",
            authority="challenge-package",
            effective_at="2026-07-10",
            as_of="2026-08-01T08:00:00Z",
            facts={"status": "quality_hold"},
        )
        self.assertIsInstance(item, EvidenceItem)
        self.assertEqual(item["retrieved_at"], "2026-08-01T08:00:00Z")
        self.assertEqual(item["effective_at"], "2026-07-10")
        self.assertTrue(item["integrity"]["source_preserved"])

    def test_unknown_source_abstains(self) -> None:
        result = build_evidence_item(
            source="data/does_not_exist.csv",
            record_id="x",
            authority="challenge-package",
            effective_at=None,
            as_of="2026-08-01T08:00:00Z",
            facts={},
        )
        self.assertIsInstance(result, Abstention)
        self.assertEqual(result.reason_code, "INTEGRITY_FAILED")
