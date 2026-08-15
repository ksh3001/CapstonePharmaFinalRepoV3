from __future__ import annotations

import json
import unittest

from packages.kernel.packs import pv_pack
from tests.helpers import load_pub


class ListednessTests(unittest.TestCase):
    def test_pub06_is_jurisdiction_qualified_and_cites_ib_ccds_local(self) -> None:
        pack = pv_pack(load_pub("PUB-06"), case_ids=["NCB-204"])
        rows = pack["listedness_context"]
        self.assertTrue(rows)
        classes = {item.get("source_class") for item in rows}
        self.assertIn("IB", classes)
        self.assertIn("CCDS", classes)
        self.assertIn("local_label", classes)
        for item in rows:
            self.assertTrue(item.get("jurisdiction"))
            self.assertTrue(item.get("source_document"))
            self.assertNotIn("expectedness", item)
            self.assertNotIn("expected", item)

    def test_listedness_disagreement_is_preserved_without_expectedness(self) -> None:
        pack = pv_pack(load_pub("PUB-06"), case_ids=["NCB-204"])
        listed = {(item.get("source_document"), item.get("listed")) for item in pack["listedness_context"] if "listed" in item}
        self.assertIn(("IB v12", "yes"), listed)
        self.assertIn(("CCDS v4", "yes"), listed)
        self.assertIn(("IN local label", "no"), listed)
        rendered = json.dumps(pack).lower()
        self.assertNotIn("event is expected", rendered)
        self.assertNotIn("expectedness", rendered)
        disagreement = [item for item in pack["contradictions"] if item.get("topic") == "listedness"]
        self.assertTrue(disagreement)
        values = set(disagreement[0].get("values") or [])
        self.assertEqual(values, {"yes", "no"})
