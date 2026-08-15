from __future__ import annotations

import unittest

from packages.kernel.packs import pv_pack
from tests.helpers import load_pub


class LanguageScopeTests(unittest.TestCase):
    def test_arabic_case_abstains_and_names_the_subgroup(self) -> None:
        pack = pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
        language = [
            item
            for item in pack["abstentions"]
            if item.get("reason_code") == "language_out_of_scope" and item.get("subject_id") == "PV-1014"
        ]
        self.assertTrue(language, pack["abstentions"])
        self.assertEqual(language[0].get("language"), "Arabic")
        limitations = pack.get("human_review", {}).get("subgroup_limitations") or []
        named = " ".join(str(item) for item in limitations).lower()
        self.assertIn("arabic", named)
        german = [
            item
            for item in pack["abstentions"]
            if item.get("reason_code") == "language_out_of_scope" and item.get("subject_id") == "PV-1001"
        ]
        english = [
            item
            for item in pack["abstentions"]
            if item.get("reason_code") == "language_out_of_scope" and item.get("subject_id") == "PV-1009"
        ]
        self.assertFalse(german)
        self.assertFalse(english)

    def test_hindi_limitation_is_stated_from_metrics(self) -> None:
        pack = pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
        limitations = pack.get("human_review", {}).get("subgroup_limitations") or []
        named = " ".join(str(item) for item in limitations).lower()
        self.assertIn("hindi", named)
