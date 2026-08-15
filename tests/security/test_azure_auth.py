from __future__ import annotations

import os
import unittest

from packages.config.runtime import inference_allowed
from packages.kernel.checkpoint import reset_replay
from services.integration.azure.openai import AzureOpenAIAdapter


class AzureAuthTests(unittest.TestCase):
    def test_key_auth_is_refused_outside_dev(self) -> None:
        reset_replay()
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
                "AZURE_OPENAI_API_KEY",
                "AEGIS_ALLOW_KEY_AUTH",
            )
        }
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "advisory"
            os.environ["AEGIS_LLM_ENABLED"] = "true"
            os.environ["AZURE_OPENAI_ENDPOINT"] = "https://example.openai.azure.com"
            os.environ["AZURE_OPENAI_DEPLOYMENT"] = "dep"
            os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-15-preview"
            os.environ["AZURE_OPENAI_MODEL_VERSION"] = "2024-05-01"
            os.environ["AZURE_OPENAI_REGION"] = "eu"
            os.environ["AZURE_OPENAI_API_KEY"] = "not-a-real-key"
            os.environ.pop("AEGIS_ALLOW_KEY_AUTH", None)
            self.assertTrue(inference_allowed())
            result = AzureOpenAIAdapter().generate({"evidence": [], "authorization": {}})
            self.assertEqual(result["outbound"], 0)
            self.assertEqual(result["reason"], "key_auth_forbidden")
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
