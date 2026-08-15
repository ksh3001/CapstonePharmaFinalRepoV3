from __future__ import annotations

import unittest

from packages.advice.guards import guard_advice


class GuardNumericClosureTests(unittest.TestCase):
    def test_number_absent_from_pack_is_g3(self) -> None:
        pack = {"evidence": [{"record_id": "E-1"}], "abstentions": []}
        result = guard_advice(pack, {"text": "Yield is 99.9", "evidence_refs": ["E-1"]})
        self.assertFalse(result["passed"])
        self.assertEqual(result["check"], "G-3")
        self.assertIsNone(result["advice"])
