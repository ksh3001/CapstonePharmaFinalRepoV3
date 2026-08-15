from __future__ import annotations

import os
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from services.integration.azure.openai import AzureOpenAIAdapter
from tests.helpers import load_pub


class ModelMetadataTests(unittest.TestCase):
    def test_configured_adapter_records_deployment_version_and_fingerprint(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-13"))
        old = {key: os.environ.get(key) for key in (
            "AEGIS_RUNTIME_MODE",
            "AEGIS_LLM_ENABLED",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_MODEL_VERSION",
            "AZURE_OPENAI_REGION",
        )}
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "advisory"
            os.environ["AEGIS_LLM_ENABLED"] = "true"
            os.environ["AZURE_OPENAI_ENDPOINT"] = "https://example.openai.azure.com"
            os.environ["AZURE_OPENAI_DEPLOYMENT"] = "ncb204-advisory"
            os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-15-preview"
            os.environ["AZURE_OPENAI_MODEL_VERSION"] = "2024-05-13"
            os.environ["AZURE_OPENAI_REGION"] = "eu"
            result = AzureOpenAIAdapter().generate(pack)
            self.assertTrue(result["called"])
            self.assertEqual(result["deployment"], "ncb204-advisory")
            self.assertEqual(result["model_version"], "2024-05-13")
            self.assertEqual(result["api_version"], "2024-02-15-preview")
            self.assertEqual(result["system_fingerprint"], "fp-assessment")
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
