from __future__ import annotations

import os
import unittest

from packages.config.runtime import inference_allowed, llm_enabled, runtime_mode
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.lifecycle import start_request
from packages.kernel.packs import advisory_pack, batch_pack, pv_pack, supply_pack
from tests.helpers import load_pub


class AiDisabledTests(unittest.TestCase):
    def test_kill_switch_default(self) -> None:
        old_mode = os.environ.get("AEGIS_RUNTIME_MODE")
        old_llm = os.environ.get("AEGIS_LLM_ENABLED")
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "assessment"
            os.environ["AEGIS_LLM_ENABLED"] = "false"
            self.assertEqual(runtime_mode(), "assessment")
            self.assertFalse(llm_enabled())
            self.assertFalse(inference_allowed())
            started = start_request(
                {
                    "user": "participant_test_user",
                    "purpose": "capstone_evaluation",
                    "as_of": "2026-08-01T08:00:00Z",
                    "execution": "disabled",
                },
                scenario_id="PUB-01",
            )
            self.assertEqual(started["execution_status"], "not_executed")
            self.assertFalse(started["llm_enabled"])
        finally:
            for key, value in (("AEGIS_RUNTIME_MODE", old_mode), ("AEGIS_LLM_ENABLED", old_llm)):
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_ai_disabled_still_emits_schema_valid_batch_pack(self) -> None:
        from packages.kernel.checkpoint import reset_replay

        reset_replay()
        old_mode = os.environ.get("AEGIS_RUNTIME_MODE")
        old_llm = os.environ.get("AEGIS_LLM_ENABLED")
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "ai_disabled"
            os.environ["AEGIS_LLM_ENABLED"] = "false"
            pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
            validate(pack, resolve_contract("batch_response.schema.json"))
            self.assertEqual(pack["execution_status"], "not_executed")
            self.assertFalse(llm_enabled())
            pv = pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
            validate(pv, resolve_contract("pv_response.schema.json"))
            self.assertEqual(pv["execution_status"], "not_executed")
            supply = supply_pack(load_pub("PUB-07"), event_id="NCB-204-shortage")
            validate(supply, resolve_contract("supply_response.schema.json"))
            self.assertEqual(supply["execution_status"], "not_executed")
            self.assertTrue(supply["no_side_effects"])
            clinical = advisory_pack(load_pub("PUB-15"))
            validate(clinical, resolve_contract("advisory_nonexecuting"))
            self.assertEqual(clinical["execution_status"], "not_executed")
            reliability = advisory_pack(load_pub("PUB-10"))
            validate(reliability, resolve_contract("advisory_nonexecuting"))
            self.assertEqual(reliability["execution_status"], "not_executed")
            self.assertEqual(reliability["workflow"], "reliability")
            finops = advisory_pack(load_pub("PUB-14"))
            validate(finops, resolve_contract("advisory_nonexecuting"))
            self.assertEqual(finops["execution_status"], "not_executed")
            privacy = advisory_pack(load_pub("PUB-09"))
            validate(privacy, resolve_contract("advisory_nonexecuting"))
            self.assertEqual(privacy["execution_status"], "not_executed")
            self.assertEqual(privacy["authorization"]["decision"], "allow")
            agent = advisory_pack(load_pub("PUB-13"))
            validate(agent, resolve_contract("advisory_nonexecuting"))
            self.assertEqual(agent["execution_status"], "not_executed")
            self.assertFalse(inference_allowed())
        finally:
            for key, value in (("AEGIS_RUNTIME_MODE", old_mode), ("AEGIS_LLM_ENABLED", old_llm)):
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
