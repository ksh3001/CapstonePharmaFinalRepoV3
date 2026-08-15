from __future__ import annotations

import unittest

from packages.contracts.deny import assert_clean, grade
from packages.contracts.invariants import assert_invariants
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.packs import supply_pack
from tests.helpers import load_pub


class SupplyContractTests(unittest.TestCase):
    def test_pub_07_and_08_validate(self) -> None:
        schema = resolve_contract("supply_response.schema.json")
        cases = (("PUB-07", "NCB-204-shortage"), ("PUB-08", "SH-901"))
        for name, event_id in cases:
            with self.subTest(name=name):
                pack = supply_pack(load_pub(name), event_id=event_id)
                validate(pack, schema)
                self.assertEqual(pack["workflow"], "supply_options")
                self.assertEqual(pack["execution_status"], "not_executed")
                self.assertTrue(pack["no_side_effects"])
                self.assertEqual(pack["event_id"], event_id)
                for option in pack["options"]:
                    self.assertEqual(option["status"], "draft")
                assert_invariants(pack)
                self.assertEqual(grade(pack), [])
                assert_clean(pack)
