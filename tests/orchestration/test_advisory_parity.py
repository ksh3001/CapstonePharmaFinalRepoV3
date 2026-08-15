from __future__ import annotations

import os
import unittest

from packages.advice.resolve import reset_inference_port, set_inference_port
from packages.kernel.canonical import dumps
from packages.kernel.checkpoint import reset_replay
from packages.orchestrator.deterministic import StdlibOrchestrator
from services.integration.azure.openai import AzureOpenAIAdapter
from tests.helpers import load_pub


def _strip_annotations(pack: dict) -> bytes:
    clone = dict(pack)
    review = dict(clone.get("human_review") or {})
    review.pop("annotations", None)
    clone["human_review"] = review
    return dumps(clone)


class AdvisoryParityTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_inference_port()

    def tearDown(self) -> None:
        reset_inference_port()
        for key in (
            "AEGIS_RUNTIME_MODE",
            "AEGIS_LLM_ENABLED",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_MODEL_VERSION",
            "AZURE_OPENAI_REGION",
        ):
            os.environ.pop(key, None)

    def test_advisory_pack_matches_assessment_once_annotations_are_stripped(self) -> None:
        fixture = load_pub("PUB-13")
        os.environ["AEGIS_RUNTIME_MODE"] = "assessment"
        os.environ["AEGIS_LLM_ENABLED"] = "false"
        reset_replay()
        offline = StdlibOrchestrator().run({"fixture": fixture})
        os.environ["AEGIS_RUNTIME_MODE"] = "advisory"
        os.environ["AEGIS_LLM_ENABLED"] = "true"
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://example.openai.azure.com"
        os.environ["AZURE_OPENAI_DEPLOYMENT"] = "dep"
        os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-15-preview"
        os.environ["AZURE_OPENAI_MODEL_VERSION"] = "2024-05-01"
        os.environ["AZURE_OPENAI_REGION"] = "eu"
        set_inference_port(AzureOpenAIAdapter())
        reset_replay()
        advisory = StdlibOrchestrator().run({"fixture": fixture})
        self.assertIn("annotations", advisory.get("human_review") or {})
        self.assertNotIn("annotations", offline.get("human_review") or {})
        self.assertEqual(_strip_annotations(advisory), dumps(offline))
