from __future__ import annotations

import unittest

from packages.advice.guards import guard_advice


class GuardDenyListTests(unittest.TestCase):
    def test_disposition_language_is_g1_and_pack_still_usable(self) -> None:
        pack = {"evidence": [{"record_id": "E-1"}], "abstentions": [], "execution_status": "not_executed"}
        result = guard_advice(pack, {"text": "Lot is approved for release.", "evidence_refs": ["E-1"]})
        self.assertFalse(result["passed"])
        self.assertEqual(result["check"], "G-1")
        self.assertEqual(pack["execution_status"], "not_executed")

    def test_additional_properties_are_g4(self) -> None:
        pack = {"evidence": [{"record_id": "E-1"}], "abstentions": []}
        result = guard_advice(pack, {"text": "Summary.", "evidence_refs": ["E-1"], "extra": True})
        self.assertFalse(result["passed"])
        self.assertEqual(result["check"], "G-4")
