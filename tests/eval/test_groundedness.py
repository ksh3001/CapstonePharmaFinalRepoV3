from __future__ import annotations

import unittest

from evals.graders.deterministic.groundedness import groundedness


class GroundednessTests(unittest.TestCase):
    def test_unsupported_claim_fails_l6a(self) -> None:
        pack = {"evidence": [{"record_id": "E-1"}], "abstentions": []}
        result = groundedness("Yield is 99.9", pack)
        self.assertEqual(result["level"], "L6a")
        self.assertFalse(result["passed"])

    def test_supported_text_passes(self) -> None:
        pack = {"evidence": [{"record_id": "E-1"}], "abstentions": []}
        result = groundedness("Model-generated summary of the pack.", pack)
        self.assertTrue(result["passed"])
