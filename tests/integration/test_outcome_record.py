from __future__ import annotations

import unittest

from packages.evidence_store.chain import load_chain, reset_store
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack, batch_pack
from tests.helpers import load_pub


class OutcomeRecordTests(unittest.TestCase):
    def test_one_outcome_per_request_from_closed_set(self) -> None:
        reset_replay()
        reset_store()
        packs = [
            batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071"),
            advisory_pack(load_pub("PUB-10")),
        ]
        allowed = {
            "completed",
            "abstained",
            "denied",
            "budget_exhausted",
            "source_unavailable",
            "contract_invalid",
            "guard_failed",
            "timeout",
            "internal_error",
        }
        for pack in packs:
            rows = load_chain(pack["request_id"])
            requests = [row for row in rows if row["type"] == "request"]
            outcomes = [row for row in rows if row["type"] == "outcome"]
            self.assertEqual(len(requests), 1)
            self.assertEqual(len(outcomes), 1)
            self.assertIn(outcomes[0]["payload"]["disposition"], allowed)
