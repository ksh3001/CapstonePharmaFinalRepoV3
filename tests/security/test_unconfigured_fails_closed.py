from __future__ import annotations

import os
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from services.integration.azure.openai import AzureOpenAIAdapter
from tests.helpers import load_pub


class UnconfiguredFailsClosedTests(unittest.TestCase):
    def test_missing_settings_make_zero_calls(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-13"))
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
            )
        }
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "advisory"
            os.environ["AEGIS_LLM_ENABLED"] = "true"
            for key in (
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_DEPLOYMENT",
                "AZURE_OPENAI_API_VERSION",
                "AZURE_OPENAI_MODEL_VERSION",
                "AZURE_OPENAI_REGION",
            ):
                os.environ.pop(key, None)
            result = AzureOpenAIAdapter().generate(pack)
            self.assertEqual(result["outbound"], 0)
            self.assertIn("unconfigured", result["reason"])
            self.assertIsNone(result["annotations"])
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
