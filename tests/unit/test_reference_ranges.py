from __future__ import annotations

import unittest

from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class ReferenceRangeTests(unittest.TestCase):
    def test_all_three_uln_values_are_retained_as_contradiction(self) -> None:
        pack = advisory_pack(load_pub("PUB-15"))
        cold = [item for item in pack["contradictions"] if item.get("topic") == "reference_range"]
        self.assertTrue(cold)
        limits = cold[0].get("limits") or {}
        self.assertEqual(str(limits.get("central_uln")), "40")
        self.assertEqual(str(limits.get("local_uln")), "60")
        self.assertEqual(str(limits.get("edc_rule_uln")), "40")
        self.assertEqual(cold[0].get("value"), "58")

    def test_range_dependent_outcomes_are_not_ranked(self) -> None:
        pack = advisory_pack(load_pub("PUB-15"))
        rows = pack["human_review"]["clinical"]["reference_range_outcomes"]
        self.assertTrue(rows)
        outcomes = rows[0]["outcomes"]
        by_limit = {item["limit"]: item for item in outcomes}
        self.assertTrue(by_limit["central_uln"]["exceeds_this_limit"])
        self.assertFalse(by_limit["local_uln"]["exceeds_this_limit"])
        self.assertTrue(by_limit["edc_rule_uln"]["exceeds_this_limit"])
        rendered = str(pack)
        self.assertNotIn("selected_limit", rendered)
        self.assertNotIn("preferred_range", rendered)
        self.assertNotIn("ranking", rendered.casefold())
