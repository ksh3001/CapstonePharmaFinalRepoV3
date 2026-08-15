from __future__ import annotations

import unittest

from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with


class StatusVocabularyTests(unittest.TestCase):
    def test_status_and_lifecyclestate_are_not_equated(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/api_contract_versions.csv",
                    "records": [
                        {"api": "LIMS result", "version": "v1", "status_field": "status"},
                        {"api": "LIMS result", "version": "v2", "status_field": "lifecycleState"},
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
            scenario_id="SYN-STATUS",
            workflow="integration",
        )
        pack = advisory_pack(fixture)
        topics = [item.get("topic") for item in pack["contradictions"]]
        self.assertIn("status_vocabulary", topics)
        rendered = str(pack).casefold()
        self.assertNotIn("status equivalent", rendered)
        presented = pack["human_review"]["interface_reconciliation"]["presented"]
        v1 = next(item for item in presented if item.get("record_id") == "LR-88")
        v2 = next(item for item in presented if item.get("record_id") == "LR-V2")
        self.assertEqual(v1["status"], "OOS_LIMS")
        self.assertEqual(v1["status_field"], "status")
        self.assertEqual(v2["lifecycleState"], "inReview")
        self.assertEqual(v2["status_field"], "lifecycleState")
