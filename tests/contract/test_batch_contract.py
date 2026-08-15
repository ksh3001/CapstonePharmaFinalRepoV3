from __future__ import annotations

import unittest

from packages.contracts.deny import assert_clean
from packages.contracts.invariants import assert_invariants
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.packs import batch_pack
from tests.helpers import load_pub, walk_converted


BATCH_IDS = {
    "PUB-01": "NCB204-B24071",
    "PUB-02": "NCS310-S26033",
    "PUB-03": "NCB204-B24071",
}


class BatchContractTests(unittest.TestCase):
    def test_pub_01_02_03_validate(self) -> None:
        schema = resolve_contract("batch_response.schema.json")
        for name, batch_id in BATCH_IDS.items():
            with self.subTest(name=name):
                pack = batch_pack(load_pub(name), batch_id=batch_id)
                validate(pack, schema)
                self.assertEqual(pack["workflow"], "batch_evidence")
                self.assertEqual(pack["execution_status"], "not_executed")
                self.assertEqual(pack["batch_id"], batch_id)
                assert_invariants(pack)
                assert_clean(pack)

    def test_evidence_items_carry_provenance(self) -> None:
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        self.assertTrue(pack["evidence"])
        for item in pack["evidence"]:
            self.assertTrue(item["source"])
            self.assertTrue(item["record_id"])
            self.assertTrue(item["authority"])
            self.assertEqual(item["retrieved_at"], "2026-08-01T08:00:00Z")
            self.assertRegex(item["integrity"]["sha256"], r"^[a-f0-9]{64}$")
            self.assertIs(item["integrity"]["source_preserved"], True)

    def test_pub01_has_no_converted_number(self) -> None:
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        self.assertEqual(walk_converted(pack), [])
