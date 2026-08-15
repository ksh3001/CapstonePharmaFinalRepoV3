from __future__ import annotations

import unittest

from packages.domain.supply import RECONCILE_CALLS, reset_reconcile_calls
from packages.kernel.canonical import dumps
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack, supply_pack
from tests.helpers import load_pub


class IdempotentReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_reconcile_calls()

    def test_supply_replay_returns_original_pack_without_recompute(self) -> None:
        fixture = load_pub("PUB-07")
        first = supply_pack(fixture, event_id="NCB-204-shortage")
        after_first = RECONCILE_CALLS
        second = supply_pack(fixture, event_id="NCB-204-shortage")
        self.assertEqual(RECONCILE_CALLS, after_first)
        self.assertEqual(dumps(first), dumps(second))
        self.assertTrue(first["no_side_effects"])

    def test_ar77_resume_does_not_create_a_third_draft(self) -> None:
        fixture = load_pub("PUB-13")
        first = advisory_pack(fixture)
        drafts = first["human_review"]["preexisting_drafts"]
        ids = [item["draft_id"] for item in drafts]
        self.assertEqual(ids, ["DR-1", "DR-2"])
        self.assertEqual(first["human_review"]["draft_count"], 2)
        for item in drafts:
            self.assertEqual(item["status"], "draft")
        second = advisory_pack(fixture)
        self.assertEqual(dumps(first), dumps(second))
        self.assertEqual(second["human_review"]["draft_count"], 2)
        rendered = str(second)
        self.assertNotIn("DR-3", rendered)
        self.assertTrue(second["no_side_effects"])
