from __future__ import annotations

import unittest

from packages.kernel.packs import batch_pack
from tests.helpers import load_pub


class BatchContradictionTests(unittest.TestCase):
    def test_genealogy_retains_both_mes_and_warehouse_values(self) -> None:
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        genealogy = [item for item in pack["contradictions"] if item.get("topic") == "genealogy"]
        self.assertTrue(genealogy, pack["contradictions"])
        values = set()
        refs = set()
        for item in genealogy:
            values.update(str(value) for value in item.get("values") or [])
            refs.update(item.get("evidence_refs") or [])
            left = item.get("left") or {}
            right = item.get("right") or {}
            values.add(str(left.get("value") or ""))
            values.add(str(right.get("value") or ""))
            if left.get("record_id"):
                refs.add(left["record_id"])
            if right.get("record_id"):
                refs.add(right["record_id"])
        self.assertIn("missing_branch", values)
        self.assertIn("issued", values)
        evidence_ids = {item["record_id"] for item in pack["evidence"]}
        self.assertTrue(refs)
        self.assertTrue(refs <= evidence_ids, refs - evidence_ids)

    def test_oos_states_are_retained(self) -> None:
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        oos = [item for item in pack["contradictions"] if item.get("topic") == "oos_status"]
        self.assertTrue(oos)
        values = set(oos[0].get("values") or [])
        self.assertEqual(values, {"OOS", "OOT"})
        self.assertEqual(oos[0].get("notebook_state"), "invalid_sample_prep")
        self.assertEqual(oos[0].get("final_state"), "open")
