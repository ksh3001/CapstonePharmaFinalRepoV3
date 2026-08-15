from __future__ import annotations

import unittest

from packages.advice.guards import guard_advice


class GuardAbstentionTests(unittest.TestCase):
    def test_narrating_past_abstention_is_g5(self) -> None:
        pack = {
            "evidence": [{"record_id": "E-1"}],
            "abstentions": [{"reason_code": "unit_unmapped", "subject_id": "LR-88"}],
        }
        result = guard_advice(pack, {"text": "No issue remains for this unit.", "evidence_refs": ["E-1"]})
        self.assertFalse(result["passed"])
        self.assertEqual(result["check"], "G-5")
