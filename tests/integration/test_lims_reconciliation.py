from __future__ import annotations

import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with, load_pub, walk_converted


class LimsReconciliationTests(unittest.TestCase):
    def test_pub12_states_versions_and_source_units(self) -> None:
        pack = advisory_pack(load_pub("PUB-12"))
        validate(pack, resolve_contract("advisory_nonexecuting"))
        review = pack["human_review"]["interface_reconciliation"]
        versions = set(review["contract_versions"])
        self.assertIn("v1", versions)
        self.assertIn("v2", versions)
        presented = review["presented"]
        units = {item.get("source_unit") for item in presented} | {item.get("target_unit") for item in presented}
        self.assertIn("mg/L", units)
        self.assertIn("ug/mL", units)
        self.assertTrue(any(item.get("contract_version") == "v1" for item in presented))
        self.assertTrue(any(item.get("contract_version") == "v2" for item in presented))
        self.assertEqual(walk_converted(pack), [])

    def test_v1_and_v2_results_retain_source_units_and_values(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/api_contract_versions.csv",
                    "records": [
                        {"api": "LIMS result", "version": "v1", "unit_field": "unit", "status_field": "status"},
                        {
                            "api": "LIMS result",
                            "version": "v2",
                            "unit_field": "ucum_code",
                            "status_field": "lifecycleState",
                        },
                    ],
                },
                {
                    "source": "data/interface_mappings.csv",
                    "records": [
                        {
                            "interface": "CRO_LAB_TO_LIMS",
                            "source_unit": "mg/L",
                            "target_unit": "ug/mL",
                            "conversion_rule": "1:1_assumed",
                            "approved": "no",
                        }
                    ],
                },
                {
                    "source": "data/lab_results.csv",
                    "records": [
                        {
                            "result_id": "LR-88",
                            "contract_version": "v1",
                            "value": "0.92",
                            "unit": "mg/L",
                            "status": "OOS_LIMS",
                        },
                        {
                            "result_id": "LR-V2",
                            "contract_version": "v2",
                            "numericValue": "0.92",
                            "ucum_code": "ug/mL",
                            "lifecycleState": "inReview",
                        },
                    ],
                },
            ],
            scenario_id="SYN-LIMS",
            workflow="integration",
        )
        pack = advisory_pack(fixture)
        presented = pack["human_review"]["interface_reconciliation"]["presented"]
        v1 = next(item for item in presented if item.get("record_id") == "LR-88")
        v2 = next(item for item in presented if item.get("record_id") == "LR-V2")
        self.assertEqual(v1["contract_version"], "v1")
        self.assertEqual(v1["unit"], "mg/L")
        self.assertEqual(v1["value"], "0.92")
        self.assertEqual(v1["unit_field"], "unit")
        self.assertNotIn("ucum_code", v1)
        self.assertEqual(v2["contract_version"], "v2")
        self.assertEqual(v2["ucum_code"], "ug/mL")
        self.assertEqual(v2["value"], "0.92")
        self.assertEqual(v2["unit_field"], "ucum_code")
        self.assertEqual(walk_converted(pack), [])
