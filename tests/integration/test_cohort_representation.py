from __future__ import annotations

import json
import unittest

from packages.kernel.packs import pv_pack
from tests.helpers import load_pub


class CohortRepresentationTests(unittest.TestCase):
    def test_underrepresented_group_b_is_named_with_the_comparison(self) -> None:
        pack = pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
        limitations = pack.get("human_review", {}).get("subgroup_limitations") or []
        omics = [
            item
            for item in limitations
            if item.get("subgroup") == "Group-B" or "group-b" in str(item).casefold()
        ]
        self.assertTrue(omics, limitations)
        statement = json.dumps(omics).lower()
        self.assertIn("group-b", statement)
        self.assertIn("group-a", statement)
        self.assertTrue("0.61" in statement or "auroc" in statement)
        rendered = json.dumps(pack).lower()
        self.assertNotIn("generalises to all ancestries", rendered)
        self.assertNotIn("signal confirmed", rendered)
        for item in pack["evidence"]:
            facts = item.get("facts") or {}
            if facts.get("model_id") == "TRN-OMICS-2" and facts.get("slice") == "Group-B":
                self.assertTrue(facts.get("limitations"))
