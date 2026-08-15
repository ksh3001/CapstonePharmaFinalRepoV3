from __future__ import annotations

import json
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with


class ModelQualificationTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_unqualified_model_is_refused_and_names_missing_qualification(self) -> None:
        payload = fixture_with(
            [
                {
                    "source": "data/model_endpoints.csv",
                    "records": [
                        {
                            "model_id": "research-disco-9",
                            "intended_use": "discovery_screening",
                            "qualification": "locked training set for discovery_screening",
                        }
                    ],
                }
            ],
            scenario_id="MODEL-UNQUAL",
            workflow="security",
        )
        pack = advisory_pack(payload)
        findings = [item for item in pack["findings"] if item.get("finding_id") == "F-MODEL-research-disco-9"]
        self.assertTrue(findings)
        statement = findings[0]["statement"].casefold()
        self.assertIn("missing qualification", statement)
        self.assertIn("discovery_screening", statement)
        self.assertEqual(pack["human_review"]["tools"]["derived_output"], [])
        rendered = json.dumps(pack)
        self.assertNotIn("model_output", rendered)

    def test_validated_for_another_purpose_uses_the_same_refusal(self) -> None:
        payload = fixture_with(
            [
                {
                    "source": "data/model_endpoints.csv",
                    "records": [
                        {
                            "model_id": "pv-extract-1",
                            "intended_use": "pv_intake",
                            "validated_for": "pv_intake",
                            "qualification": "validated for pv_intake only",
                        }
                    ],
                }
            ],
            scenario_id="MODEL-OTHER",
            workflow="security",
        )
        pack = advisory_pack(payload)
        findings = [item for item in pack["findings"] if item.get("finding_id") == "F-MODEL-pv-extract-1"]
        self.assertTrue(findings)
        self.assertIn("missing qualification", findings[0]["statement"].casefold())
        abstentions = [item for item in pack["abstentions"] if item.get("reason_code") == "model_unqualified"]
        self.assertTrue(abstentions)
        self.assertEqual(pack["human_review"]["tools"]["derived_output"], [])
