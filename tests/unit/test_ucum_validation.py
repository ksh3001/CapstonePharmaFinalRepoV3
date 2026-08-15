from __future__ import annotations

import unittest

from packages.ontology.ucum import ucum_valid
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with


class UcumValidationTests(unittest.TestCase):
    def test_v1_free_text_is_not_emitted_as_ucum(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/lab_results.csv",
                    "records": [
                        {
                            "result_id": "LR-88",
                            "contract_version": "v1",
                            "value": "0.92",
                            "unit": "mg/L",
                            "status": "OOS_LIMS",
                        }
                    ],
                }
            ],
            scenario_id="SYN-UCUM-V1",
            workflow="integration",
        )
        pack = advisory_pack(fixture)
        presented = pack["human_review"]["interface_reconciliation"]["presented"]
        v1 = next(item for item in presented if item.get("record_id") == "LR-88")
        self.assertEqual(v1["unit_field"], "unit")
        self.assertEqual(v1["unit"], "mg/L")
        self.assertNotIn("ucum_code", v1)

    def test_invalid_ucum_is_reported_and_record_is_kept(self) -> None:
        self.assertFalse(ucum_valid("not-a-ucum"))
        fixture = fixture_with(
            [
                {
                    "source": "data/lab_results.csv",
                    "records": [
                        {
                            "result_id": "LR-BAD",
                            "contract_version": "v2",
                            "numericValue": "1.0",
                            "ucum_code": "not-a-ucum",
                            "lifecycleState": "inReview",
                        }
                    ],
                }
            ],
            scenario_id="SYN-UCUM-BAD",
            workflow="integration",
        )
        pack = advisory_pack(fixture)
        statements = [str(item.get("statement") or "") for item in pack["findings"]]
        self.assertTrue(any("invalid" in item.casefold() and "not-a-ucum" in item for item in statements))
        presented = pack["human_review"]["interface_reconciliation"]["presented"]
        kept = next(item for item in presented if item.get("record_id") == "LR-BAD")
        self.assertEqual(kept["ucum_code"], "not-a-ucum")
        self.assertEqual(kept["value"], "1.0")
