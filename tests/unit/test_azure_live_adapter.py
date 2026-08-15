from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from packages.kernel.checkpoint import reset_replay
from services.integration.azure.openai import AzureOpenAIAdapter


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


class AzureLiveAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        self._old = {
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
                "GENERATOR_DEPLOYMENT",
            )
        }

    def tearDown(self) -> None:
        for key, value in self._old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def _advisory(self) -> None:
        os.environ["AEGIS_RUNTIME_MODE"] = "advisory"
        os.environ["AEGIS_LLM_ENABLED"] = "true"
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://openaiksh.openai.azure.com"
        os.environ["AZURE_OPENAI_DEPLOYMENT"] = "gpt-4.1"
        os.environ["AZURE_OPENAI_API_VERSION"] = "2024-12-01-preview"
        os.environ["AZURE_OPENAI_MODEL_VERSION"] = "gpt-4.1"
        os.environ["AZURE_OPENAI_REGION"] = "eastus"
        os.environ["AZURE_OPENAI_API_KEY"] = "not-a-real-key"
        os.environ["AEGIS_ALLOW_KEY_AUTH"] = "dev"

    def test_example_host_stays_on_stub_even_with_key(self) -> None:
        self._advisory()
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://example.openai.azure.com"
        with patch("urllib.request.urlopen") as mocked:
            result = AzureOpenAIAdapter().generate({"evidence": [], "authorization": {}})
        mocked.assert_not_called()
        self.assertTrue(result["called"])
        self.assertEqual(result["system_fingerprint"], "fp-assessment")
        self.assertEqual(result["prompt_tokens"], 0)
        self.assertEqual(result["completion_tokens"], 0)
        self.assertEqual(result["total_tokens"], 0)

    def test_stub_summary_cites_evidence_on_example_host(self) -> None:
        self._advisory()
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://example.openai.azure.com"
        pack = {
            "evidence": [{"record_id": "LAB-1", "source": "lab", "facts": {"assay": "98"}}],
            "gaps": [{"gap_type": "cmo_commitment_missing"}],
            "contradictions": [],
            "abstentions": [],
            "authorization": {},
        }
        with patch("urllib.request.urlopen") as mocked:
            result = AzureOpenAIAdapter().generate(pack)
        mocked.assert_not_called()
        advice = result["annotations"]
        self.assertIsNotNone(advice)
        self.assertIn("LAB-1", advice["text"])
        self.assertIn("LAB-1", advice["evidence_refs"])
        self.assertIn("cmo_commitment_missing", advice["text"])
        self.assertIn("instruction", result["prompt"])
        self.assertEqual(result["prompt"]["evidence"][0]["record_id"], "LAB-1")

    def test_live_json_is_guarded_and_labelled(self) -> None:
        self._advisory()
        pack = {
            "evidence": [{"record_id": "LAB-1", "statement": "assay 98"}],
            "authorization": {},
            "abstentions": [],
        }
        payload = {
            "system_fingerprint": "fp-live-test",
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "text": "Review assay 98 against LAB-1 before a human disposition.",
                                "evidence_refs": ["LAB-1"],
                            }
                        )
                    },
                    "content_filter_results": {
                        "hate": {"severity": "safe"},
                        "self_harm": {"severity": "safe"},
                        "sexual": {"severity": "safe"},
                        "violence": {"severity": "safe"},
                    },
                }
            ],
            "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
        }
        with patch("urllib.request.urlopen", return_value=_FakeResponse(payload)) as mocked:
            result = AzureOpenAIAdapter().generate(pack)
        mocked.assert_called_once()
        self.assertTrue(result["called"])
        self.assertEqual(result["outbound"], 1)
        self.assertEqual(result["system_fingerprint"], "fp-live-test")
        advice = result["annotations"]
        self.assertEqual(advice["labelled"], "model-generated")
        self.assertIn("LAB-1", advice["evidence_refs"])
        self.assertIn("assay 98", advice["text"])
        self.assertEqual(result["prompt_tokens"], 11)
        self.assertEqual(result["completion_tokens"], 7)
        self.assertEqual(result["total_tokens"], 18)
