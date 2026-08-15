from __future__ import annotations

import os
import unittest

from packages.kernel.checkpoint import reset_replay
from services.integration.azure.openai import AzureOpenAIAdapter


class ContentFilterRecordTests(unittest.TestCase):
    def test_every_call_stores_content_filter_results(self) -> None:
        reset_replay()
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
            os.environ["AZURE_OPENAI_DEPLOYMENT"] = "dep"
            os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-15-preview"
            os.environ["AZURE_OPENAI_MODEL_VERSION"] = "2024-05-01"
            os.environ["AZURE_OPENAI_REGION"] = "eu"
            result = AzureOpenAIAdapter().generate({"evidence": [], "authorization": {}})
            self.assertTrue(result["called"])
            filters = result["content_filter"]
            for key in ("hate", "self_harm", "sexual", "violence"):
                self.assertIn(key, filters)
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
