from __future__ import annotations

import unittest

from packages.domain.batch import compute_readiness
from packages.domain.types import Contradiction, Gap
from packages.kernel.packs import batch_pack
from tests.helpers import load_pub


class ReadinessStateTests(unittest.TestCase):
    def test_blocking_gap_only(self) -> None:
        gaps = [Gap(gap_type="cmo_commitment_missing", subject_id="NCB204-B24071")]
        self.assertEqual(compute_readiness(gaps, []), "insufficient_evidence")

    def test_contradiction_only(self) -> None:
        contradictions = [Contradiction(topic="genealogy", source="data/material_genealogy.csv", record_id="SUA-88")]
        self.assertEqual(compute_readiness([], contradictions), "conflicted_evidence")

    def test_gap_and_contradiction_prefer_insufficient(self) -> None:
        gaps = [Gap(gap_type="cmo_commitment_missing", subject_id="NCB204-B24071")]
        contradictions = [Contradiction(topic="genealogy", source="data/material_genealogy.csv", record_id="SUA-88")]
        self.assertEqual(compute_readiness(gaps, contradictions), "insufficient_evidence")

    def test_pub01_missing_cmo_commitment_blocks_ready(self) -> None:
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        gaps = pack["gaps"]
        self.assertTrue(
            any(
                item.get("gap_type") == "cmo_commitment_missing"
                or "CMO audit commitment" in str(item.get("packet_item") or "")
                for item in gaps
            ),
            gaps,
        )
        self.assertEqual(pack["readiness_state"], "insufficient_evidence")
        self.assertNotEqual(pack["readiness_state"], "ready_for_authorized_review")
