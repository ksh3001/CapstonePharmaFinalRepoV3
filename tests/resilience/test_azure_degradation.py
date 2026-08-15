from __future__ import annotations

import os
import unittest

from services.integration.azure.openai import AzureOpenAIAdapter


class AzureDegradationTests(unittest.TestCase):
    def test_429_then_503_yield_no_narrative_within_retry_bound(self) -> None:
        adapter = AzureOpenAIAdapter()
        old = {key: os.environ.get(key) for key in (
            "AEGIS_RUNTIME_MODE",
            "AEGIS_LLM_ENABLED",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_MODEL_VERSION",
            "AZURE_OPENAI_REGION",
            "AEGIS_AZURE_STATUS",
        )}
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "advisory"
            os.environ["AEGIS_LLM_ENABLED"] = "true"
            os.environ["AZURE_OPENAI_ENDPOINT"] = "https://example.openai.azure.com"
            os.environ["AZURE_OPENAI_DEPLOYMENT"] = "dep"
            os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-15-preview"
            os.environ["AZURE_OPENAI_MODEL_VERSION"] = "2024-05-01"
            os.environ["AZURE_OPENAI_REGION"] = "eu"
            for status in ("429", "503"):
                os.environ["AEGIS_AZURE_STATUS"] = status
                result = adapter.generate({"evidence": [], "authorization": {}})
                self.assertEqual(result["outbound"], 0)
                self.assertIsNone(result["annotations"])
                self.assertEqual(result["retries"], 1)
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
