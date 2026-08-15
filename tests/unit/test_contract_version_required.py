from __future__ import annotations

import unittest

from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with


class ContractVersionRequiredTests(unittest.TestCase):
    def test_missing_version_is_a_gap_and_is_not_inferred(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/lab_results.csv",
                    "records": [
                        {
                            "result_id": "LR-88",
                            "value": "0.92",
                            "unit": "mg/L",
                            "status": "OOS_LIMS",
                        }
                    ],
                }
            ],
            scenario_id="SYN-NOVER",
            workflow="integration",
        )
        pack = advisory_pack(fixture)
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "contract_version_missing"]
        self.assertTrue(gaps)
        self.assertEqual(gaps[0]["subject_id"], "LR-88")
        presented = pack["human_review"]["interface_reconciliation"]["presented"]
        row = next(item for item in presented if item.get("record_id") == "LR-88")
        self.assertIsNone(row.get("contract_version"))
        self.assertNotEqual(row.get("contract_version"), "v1")
        self.assertNotEqual(row.get("contract_version"), "v2")
