from __future__ import annotations

import json
import unittest

from packages.kernel.packs import pv_pack
from tests.helpers import fixture_with, CONTEXT


def _residency_fixture() -> dict:
    return fixture_with(
        [
            {
                "source": "data/data_residency.csv",
                "sha256": "placeholder",
                "records": [
                    {
                        "data_class": "EU trial personal data",
                        "approved_regions": "EU",
                        "observed_region": "SG",
                        "source": "backup_replica",
                    }
                ],
            }
        ],
        scenario_id="RES",
        workflow="pv",
    )


class ResidencyTests(unittest.TestCase):
    def test_cross_border_path_without_basis_is_denied(self) -> None:
        pack = pv_pack(_residency_fixture(), case_ids=["PV-1001"])
        self.assertEqual(pack["authorization"]["decision"], "deny")
        self.assertEqual(pack["authorization"].get("reason"), "RESIDENCY_BLOCKED")
        self.assertEqual(pack["source_facts"], [])

    def test_inference_endpoint_in_other_region_is_denied(self) -> None:
        payload = fixture_with(
            [
                {
                    "source": "data/data_residency.csv",
                    "sha256": "4eef7b490b912f9aa523571a90927b64a9c88c9ca04fbb7d74eecd426044ea76",
                    "records": [
                        {
                            "data_class": "EU trial personal data",
                            "approved_regions": "EU",
                            "observed_region": "EU",
                            "source": "primary",
                        }
                    ],
                }
            ],
            scenario_id="RES-EP",
            workflow="pv",
        )
        payload["authorized_context"] = dict(CONTEXT)
        payload["authorized_context"]["endpoint_region"] = "US"
        pack = pv_pack(payload, case_ids=["PV-1001"])
        self.assertEqual(pack["authorization"]["decision"], "deny")
        statements = json.dumps(pack.get("human_review") or {}).casefold()
        self.assertIn("endpoint", statements)


class ContinuityResidencyTests(unittest.TestCase):
    def test_pub10_region_difference_is_evaluated(self) -> None:
        from packages.kernel.checkpoint import reset_replay
        from tests.helpers import load_pub
        from packages.kernel.packs import advisory_pack

        reset_replay()
        pack = advisory_pack(load_pub("PUB-10"))
        residency = pack["human_review"]["continuity"]["residency"]
        self.assertTrue(residency["evaluated"])
        self.assertEqual(residency["outcome"], "regions_differ")
        self.assertEqual(residency["primary_region"], "EU-West")
        self.assertEqual(residency["fallback_region"], "OnPrem-DE")
        self.assertEqual(pack["authorization"]["decision"], "allow")


class AzureInferenceResidencyTests(unittest.TestCase):
    def test_region_mismatch_makes_zero_calls(self) -> None:
        import os

        from services.integration.azure.openai import AzureOpenAIAdapter

        old = {
            key: os.environ.get(key)
            for key in (
                "AEGIS_RUNTIME_MODE",
                "AEGIS_LLM_ENABLED",
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_DEPLOYMENT",
                "AZURE_OPENAI_API_VERSION",
                "AZURE_OPENAI_MODEL_VERSION",
                "AZURE_OPENAI_REGION",
                "AEGIS_DATA_REGION",
            )
        }
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "advisory"
            os.environ["AEGIS_LLM_ENABLED"] = "true"
            os.environ["AZURE_OPENAI_ENDPOINT"] = "https://example.openai.azure.com"
            os.environ["AZURE_OPENAI_DEPLOYMENT"] = "dep"
            os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-15-preview"
            os.environ["AZURE_OPENAI_MODEL_VERSION"] = "2024-05-01"
            os.environ["AZURE_OPENAI_REGION"] = "us"
            os.environ["AEGIS_DATA_REGION"] = "eu"
            result = AzureOpenAIAdapter().generate({"evidence": [], "authorization": {}})
            self.assertEqual(result["outbound"], 0)
            self.assertEqual(result["reason"], "residency_mismatch")
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

