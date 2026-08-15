from __future__ import annotations

import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with


class BackEntryFlagTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_back_entry_flag_travels_into_the_pack(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/lab_results.csv",
                    "records": [
                        {
                            "record_id": "LR-BACK",
                            "result_id": "LR-BACK",
                            "event_time": "2026-07-10",
                            "recorded_at": "2026-07-12",
                            "value": "0.92",
                            "unit": "%",
                        }
                    ],
                }
            ],
            scenario_id="SYN-BACK-ENTRY",
            workflow="security",
        )
        pack = advisory_pack(fixture)
        validate(pack, resolve_contract("advisory_nonexecuting"))
        flags = pack["human_review"]["authority"]["back_entry"]
        self.assertTrue(flags)
        self.assertTrue(flags[0]["flagged"])
        self.assertEqual(flags[0]["magnitude"], "2d")
        cited = [item for item in pack["evidence"] if item["record_id"] == "LR-BACK"]
        self.assertTrue(cited)
        payload = cited[0]["facts"]["back_entry"]
        self.assertTrue(payload["flagged"])
        self.assertEqual(payload["magnitude"], "2d")
        self.assertEqual(payload["event_time"], "2026-07-10")
        self.assertEqual(payload["recorded_at"], "2026-07-12")
