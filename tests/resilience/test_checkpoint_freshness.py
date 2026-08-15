from __future__ import annotations

import unittest

from packages.config.checkpoint import MAX_STATE_AGE_MINUTES
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack, supply_pack
from tests.helpers import CONTEXT, load_pub


class CheckpointFreshnessTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_pub13_380_minutes_is_not_auto_resumed(self) -> None:
        self.assertLess(MAX_STATE_AGE_MINUTES, 380)
        pack = advisory_pack(load_pub("PUB-13"))
        checkpoint = pack["human_review"]["checkpoint"]
        self.assertEqual(checkpoint["run_id"], "AR-77")
        self.assertEqual(checkpoint["checkpoint_id"], "cp-4")
        self.assertEqual(int(checkpoint["state_age_minutes"]), 380)
        self.assertFalse(checkpoint["fresh"])
        self.assertFalse(checkpoint["auto_resume"])
        self.assertTrue(checkpoint["human_confirmation_required"])
        self.assertTrue(
            any(item.get("reason_code") == "checkpoint_stale" for item in pack["abstentions"]),
            pack["abstentions"],
        )

    def test_hash_mismatch_blocks_resume_and_raises_a_finding(self) -> None:
        fixture = load_pub("PUB-13")
        context = dict(CONTEXT)
        context["checkpoint"] = {
            "run_id": "AR-77",
            "checkpoint_id": "cp-4",
            "input_hash": "deadbeef" * 8,
        }
        fixture["authorized_context"] = context
        pack = advisory_pack(fixture)
        checkpoint = pack["human_review"]["checkpoint"]
        self.assertFalse(checkpoint["fresh"])
        self.assertFalse(checkpoint["auto_resume"])
        self.assertEqual(checkpoint["reason"], "CHECKPOINT_HASH_MISMATCH")
        self.assertTrue(
            any("input hash" in str(item.get("statement") or "").casefold() for item in pack["findings"]),
            pack["findings"],
        )

    def test_stale_supply_checkpoint_requires_human_confirmation(self) -> None:
        fixture = load_pub("PUB-07")
        context = dict(CONTEXT)
        context["checkpoint"] = {"run_id": "SUP-1", "state_age_minutes": "380"}
        fixture["authorized_context"] = context
        pack = supply_pack(fixture, event_id="NCB-204-shortage")
        checkpoint = pack["human_review"]["checkpoint"]
        self.assertFalse(checkpoint["auto_resume"])
        self.assertTrue(checkpoint["human_confirmation_required"])
        self.assertTrue(
            any(item.get("reason_code") == "checkpoint_stale" for item in pack["abstentions"])
        )
