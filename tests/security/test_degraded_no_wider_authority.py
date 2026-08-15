from __future__ import annotations

import os
import unittest

from packages.contracts.deny import assert_clean
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack, batch_pack, pv_pack, supply_pack
from tests.helpers import load_pub


class DegradedNoWiderAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_degraded_mode_does_not_widen_automation(self) -> None:
        old_mode = os.environ.get("AEGIS_RUNTIME_MODE")
        old_llm = os.environ.get("AEGIS_LLM_ENABLED")
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "ai_disabled"
            os.environ["AEGIS_LLM_ENABLED"] = "false"
            packs = [
                advisory_pack(load_pub("PUB-10")),
                batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071"),
                pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"]),
                supply_pack(load_pub("PUB-07"), event_id="NCB-204-shortage"),
            ]
            for pack in packs:
                with self.subTest(workflow=pack.get("workflow")):
                    self.assertEqual(pack["execution_status"], "not_executed")
                    self.assertTrue(pack.get("no_side_effects", True))
                    assert_clean(pack)
            continuity = packs[0]["human_review"]["continuity"]
            self.assertFalse(continuity["automation_widened"])
            self.assertFalse(continuity["fallback_substituted"])
        finally:
            for key, value in (("AEGIS_RUNTIME_MODE", old_mode), ("AEGIS_LLM_ENABLED", old_llm)):
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
