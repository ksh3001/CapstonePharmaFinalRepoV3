from __future__ import annotations

import os
import unittest

from packages.config.runtime import inference_allowed, llm_enabled, runtime_mode
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class KillSwitchTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_kill_switch_works_when_endpoints_are_unreachable(self) -> None:
        old_mode = os.environ.get("AEGIS_RUNTIME_MODE")
        old_llm = os.environ.get("AEGIS_LLM_ENABLED")
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "ai_disabled"
            os.environ["AEGIS_LLM_ENABLED"] = "true"
            self.assertEqual(runtime_mode(), "ai_disabled")
            self.assertFalse(llm_enabled())
            self.assertFalse(inference_allowed())
            fixture = load_pub("PUB-10")
            for blob in fixture.get("evidence") or []:
                if str(blob.get("source") or "").endswith("model_endpoints.csv"):
                    for record in blob.get("records") or []:
                        record["status"] = "down"
            pack = advisory_pack(fixture)
            validate(pack, resolve_contract("advisory_nonexecuting"))
            self.assertEqual(pack["execution_status"], "not_executed")
            self.assertFalse(inference_allowed())
            from services.integration.azure.openai import AzureOpenAIAdapter

            result = AzureOpenAIAdapter().generate(pack)
            self.assertEqual(result["outbound"], 0)
            self.assertIsNone(result["annotations"])
        finally:
            for key, value in (("AEGIS_RUNTIME_MODE", old_mode), ("AEGIS_LLM_ENABLED", old_llm)):
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
