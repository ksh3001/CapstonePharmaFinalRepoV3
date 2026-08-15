from __future__ import annotations

import hashlib
import unittest

from packages.contracts.hashes import published_hash
from packages.domain.evidence import build_evidence_item, matching_published_digest
from packages.domain.types import Abstention
from packages.config.paths import synthetic_dir


class EvidenceHashTests(unittest.TestCase):
    def test_line_ending_only_difference_matches_published_digest(self) -> None:
        lf = b"col\n1\n"
        expected = hashlib.sha256(lf).hexdigest()
        self.assertTrue(matching_published_digest(lf, expected))
        self.assertTrue(matching_published_digest(b"col\r\n1\r\n", expected))
        self.assertFalse(matching_published_digest(lf + b"#tamper", expected))

    def test_synthetic_batches_csv_builds_despite_checkout_line_endings(self) -> None:
        published = published_hash("data/batches.csv")
        self.assertIsNotNone(published)
        raw = (synthetic_dir() / "data" / "batches.csv").read_bytes()
        self.assertTrue(matching_published_digest(raw, published or ""))
        item = build_evidence_item(
            source="data/batches.csv",
            record_id="NCB204-B24071",
            authority="challenge-package",
            effective_at="2026-07-10",
            as_of="2026-08-01T08:00:00Z",
            facts={"status": "quality_hold"},
        )
        self.assertNotIsInstance(item, Abstention)
        self.assertEqual(item["integrity"]["sha256"], published)
