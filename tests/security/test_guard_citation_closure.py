from __future__ import annotations

import unittest

from packages.advice.guards import guard_advice


class GuardCitationClosureTests(unittest.TestCase):
    def test_unknown_evidence_ref_is_g2(self) -> None:
        pack = {"evidence": [{"record_id": "E-1"}], "abstentions": []}
        result = guard_advice(pack, {"text": "See source.", "evidence_refs": ["E-MISSING"]})
        self.assertFalse(result["passed"])
        self.assertEqual(result["check"], "G-2")
        self.assertIsNone(result["advice"])
