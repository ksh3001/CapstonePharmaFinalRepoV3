from __future__ import annotations

import unittest

from packages.advice.brief import evidence_brief, stub_advice
from packages.advice.guards import guard_advice


class AdviceBriefTests(unittest.TestCase):
    def test_stub_summary_cites_pack_evidence(self) -> None:
        pack = {
            "batch_id": "NCB204-B24071",
            "evidence": [
                {"record_id": "LAB-1", "source": "data/lab_results.csv", "facts": {"result": "0.92"}},
            ],
            "gaps": [{"gap_type": "cmo_commitment_missing", "packet_item": "CMO audit commitment 2025-14"}],
            "contradictions": [{"topic": "genealogy", "record_id": "SUA-88"}],
            "abstentions": [{"reason_code": "unit_mismatch"}],
        }
        brief = evidence_brief(pack)
        self.assertEqual(brief["evidence"][0]["record_id"], "LAB-1")
        self.assertIn("LAB-1", str(brief))
        advice = stub_advice(pack)
        self.assertIn("LAB-1", advice["text"])
        self.assertIn("LAB-1", advice["evidence_refs"])
        self.assertIn("cmo_commitment_missing", advice["text"])
        self.assertIn("CMO audit commitment 2025-14", advice["text"])
        self.assertIn("genealogy", advice["text"])
        guarded = guard_advice(pack, advice)
        self.assertTrue(guarded["passed"], guarded)
