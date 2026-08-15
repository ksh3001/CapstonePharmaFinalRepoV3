from __future__ import annotations

import unittest
from pathlib import Path

from packages.domain.evidence import build_evidence_item
from packages.domain.types import Abstention
from packages.config.paths import synthetic_dir
from scripts.build_fixture_copyset import build


class IntegrityFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        build()

    def test_corrupt_artefact_abstains(self) -> None:
        source = "data/batches.csv"
        original = synthetic_dir() / source
        backup = original.read_bytes()
        try:
            original.write_bytes(backup + b"\n#tamper")
            result = build_evidence_item(
                source=source,
                record_id="NCB204-B24071",
                authority="challenge-package",
                effective_at=None,
                as_of="2026-08-01T08:00:00Z",
                facts={"batch_id": "NCB204-B24071"},
            )
            self.assertIsInstance(result, Abstention)
            self.assertEqual(result.reason_code, "INTEGRITY_FAILED")
            self.assertNotIn("NCB204-B24071", result.as_dict().get("facts", {}))
        finally:
            original.write_bytes(backup)

    def test_intact_artefact_preserves_published_hash(self) -> None:
        result = build_evidence_item(
            source="data/batches.csv",
            record_id="NCB204-B24071",
            authority="challenge-package",
            effective_at="2026-07-10",
            as_of="2026-08-01T08:00:00Z",
            facts={"batch_id": "NCB204-B24071"},
        )
        self.assertNotIsInstance(result, Abstention)
        self.assertEqual(result["retrieved_at"], "2026-08-01T08:00:00Z")
        self.assertTrue(result["integrity"]["source_preserved"])
        self.assertRegex(result["integrity"]["sha256"], r"^[a-f0-9]{64}$")
