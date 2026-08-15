from __future__ import annotations

import unittest

from packages.ontology.trust import can_ground_assertion, referenced_missing, trust_for_document


class TrustStatusTests(unittest.TestCase):
    def test_untrusted_instruction_cannot_ground(self) -> None:
        status = trust_for_document(status="effective", hash_ok=True, contains_instruction=True)
        self.assertEqual(status, "untrusted")
        self.assertFalse(can_ground_assertion(status))

    def test_hash_failure_is_reduced_integrity(self) -> None:
        status = trust_for_document(status="effective", hash_ok=False, contains_instruction=False)
        self.assertEqual(status, "reduced_integrity")
        self.assertFalse(can_ground_assertion(status))

    def test_draft_cannot_ground(self) -> None:
        status = trust_for_document(status="draft", hash_ok=True, contains_instruction=False)
        self.assertEqual(status, "untrusted")
        self.assertFalse(can_ground_assertion(status))

    def test_missing_reference(self) -> None:
        self.assertEqual(referenced_missing(), "referenced_missing")
        self.assertFalse(can_ground_assertion("referenced_missing"))

    def test_trusted_effective_document_can_ground(self) -> None:
        status = trust_for_document(status="effective", hash_ok=True, contains_instruction=False)
        self.assertEqual(status, "trusted")
        self.assertTrue(can_ground_assertion(status))
