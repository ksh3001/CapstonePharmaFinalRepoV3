from __future__ import annotations

import os
import unittest

from packages.evidence_store.chain import load_chain, reset_store
from packages.evidence_store.writer import persist_llm
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from services.integration.azure.openai import AzureOpenAIAdapter
from tests.helpers import load_pub


class LlmRecordTests(unittest.TestCase):
    def test_advisory_call_is_stored_without_prompt_body(self) -> None:
        reset_replay()
        reset_store()
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
            os.environ["AZURE_OPENAI_DEPLOYMENT"] = "dep"
            os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-15-preview"
            os.environ["AZURE_OPENAI_MODEL_VERSION"] = "2024-05-01"
            os.environ["AZURE_OPENAI_REGION"] = "eu"
            result = AzureOpenAIAdapter().generate(pack)
            persist_llm(pack["request_id"], result)
            rows = [row for row in load_chain(pack["request_id"]) if row["type"] == "llm"]
            self.assertEqual(len(rows), 1)
            payload = rows[0]["payload"]
            self.assertIn("prompt_sha256", payload)
            self.assertNotIn("prompt", payload)
            self.assertEqual(payload["deployment"], "dep")
            self.assertIn("content_filter", payload)
            self.assertEqual(payload["prompt_tokens"], 0)
            self.assertEqual(payload["completion_tokens"], 0)
            self.assertEqual(payload["total_tokens"], 0)
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
