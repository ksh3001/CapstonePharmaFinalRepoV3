from __future__ import annotations

import json
import unittest

from packages.kernel.packs import pv_pack
from tests.helpers import load_pub

CRITERIA = (
    "identifiable_reporter",
    "identifiable_patient",
    "suspect_product",
    "event",
)
STATES = frozenset({"present", "absent", "unverifiable"})


class ReportValidityTests(unittest.TestCase):
    def test_social_report_renders_four_criteria_without_outcome(self) -> None:
        pack = pv_pack(load_pub("PUB-05"), case_ids=["SM-77"])
        facts = [item for item in pack["source_facts"] if item.get("case_id") == "SM-77"]
        self.assertTrue(facts)
        criteria = facts[0].get("minimum_criteria") or []
        by_name = {item["criterion"]: item["state"] for item in criteria}
        self.assertEqual(set(by_name), set(CRITERIA))
        self.assertTrue(STATES.issuperset(by_name.values()))
        self.assertEqual(by_name["identifiable_reporter"], "absent")
        self.assertEqual(by_name["identifiable_patient"], "absent")
        self.assertEqual(by_name["suspect_product"], "unverifiable")
        self.assertEqual(by_name["event"], "unverifiable")
        self.assertEqual(facts[0].get("validity"), "undetermined")
        rendered = json.dumps(pack).lower()
        self.assertNotIn("auto-submit", rendered)
        self.assertNotIn('"submitted"', rendered)
        self.assertNotIn("discarded", rendered)
        self.assertNotIn("master_case", rendered)
        self.assertNotIn("merged", rendered)
        for item in pack["source_facts"]:
            self.assertNotIn("count", item)
            self.assertNotIn("n", item)
