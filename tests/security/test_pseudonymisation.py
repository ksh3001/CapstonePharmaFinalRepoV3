from __future__ import annotations

import copy
import json
import unittest

from packages.kernel.audit import audit_events, reset_audit
from packages.kernel.packs import pv_pack
from packages.kernel.privacy import pseudonym_for
from tests.helpers import load_pub


class PseudonymisationTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_audit()

    def test_direct_identifier_is_replaced_and_stable_within_purpose(self) -> None:
        fixture = load_pub("PUB-04")
        first = pv_pack(copy.deepcopy(fixture), case_ids=["PV-1001"])
        second = pv_pack(copy.deepcopy(fixture), case_ids=["PV-1001"])
        rendered = json.dumps(first)
        self.assertNotIn("P-7X", rendered)
        self.assertNotIn('"mapping"', rendered)
        keys = [item.get("patient_key") for item in first["source_facts"] if item.get("patient_key")]
        self.assertTrue(keys)
        self.assertTrue(all(str(item).startswith("PN-") or str(item).casefold() == "unknown" for item in keys))
        other_keys = [item.get("patient_key") for item in second["source_facts"] if item.get("patient_key")]
        self.assertEqual(keys, other_keys)
        expected = pseudonym_for("P-7X", "capstone_evaluation")
        self.assertIn(expected, keys)

    def test_different_purpose_yields_different_pseudonym(self) -> None:
        self.assertNotEqual(
            pseudonym_for("P-7X", "capstone_evaluation"),
            pseudonym_for("P-7X", "trial"),
        )

    def test_transformation_is_audited_without_the_mapping(self) -> None:
        pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
        events = [item for item in audit_events() if item.get("event") == "pseudonymisation"]
        self.assertTrue(events)
        self.assertNotIn("P-7X", json.dumps(events))
        self.assertNotIn("mapping", json.dumps(events))
        self.assertGreater(events[0].get("field_count"), 0)
