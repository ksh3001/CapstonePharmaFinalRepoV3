from __future__ import annotations

import unittest

from packages.contracts.deny import assert_clean
from packages.contracts.invariants import assert_invariants
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.domain.duplicates import MERGE_KEYS
from packages.kernel.packs import pv_pack
from tests.helpers import load_pub


PV_IDS = {
    "PUB-04": "PV-1001",
    "PUB-05": "SM-77",
    "PUB-06": "NCB-204",
}


class PvContractTests(unittest.TestCase):
    def test_pub_04_05_06_validate(self) -> None:
        schema = resolve_contract("pv_response.schema.json")
        for name, entity_id in PV_IDS.items():
            with self.subTest(name=name):
                pack = pv_pack(load_pub(name), case_ids=[entity_id])
                validate(pack, schema)
                self.assertEqual(pack["workflow"], "pv_intake")
                self.assertEqual(pack["execution_status"], "not_executed")
                self.assertTrue(pack["case_ids"])
                assert_invariants(pack)
                assert_clean(pack)

    def test_pub04_retains_both_meddra_versions_without_pooling(self) -> None:
        pack = pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
        versions = {item.get("version") for item in pack["terminology"]}
        dictionaries = {item.get("dictionary") for item in pack["terminology"]}
        self.assertEqual(versions, {"27.1", "28.0"})
        self.assertEqual(dictionaries, {"MedDRA"})
        rendered = str(pack)
        self.assertNotIn("pooled_count", rendered)
        self.assertNotIn("combined_count", rendered)
        for item in pack["terminology"]:
            self.assertNotIn("pooled", item)

    def test_pub04_does_not_use_source_similarity_as_score(self) -> None:
        pack = pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
        for row in pack["duplicate_candidates"]:
            self.assertIsInstance(row["score"], int)
            self.assertNotEqual(row["score"], 0.93)
            self.assertEqual(set(row) & MERGE_KEYS, set())

    def test_required_pv_arrays_are_present(self) -> None:
        pack = pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
        for key in (
            "source_facts",
            "duplicate_candidates",
            "clock_evidence",
            "terminology",
            "listedness_context",
            "required_reviews",
        ):
            self.assertIn(key, pack)
            self.assertIsInstance(pack[key], list)
