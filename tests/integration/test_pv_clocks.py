from __future__ import annotations

import unittest

from packages.kernel.packs import pv_pack
from tests.helpers import load_pub

THE_CLOCK_KEYS = frozenset(
    {
        "the_clock",
        "selected_clock",
        "chosen_clock",
        "canonical_clock",
        "primary_clock",
        "reporting_clock",
        "picked_clock",
    }
)


class PvClockTests(unittest.TestCase):
    def test_pub04_retains_every_candidate_clock(self) -> None:
        pack = pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
        clocks = [item for item in pack["clock_evidence"] if item.get("case_id") == "PV-1001"]
        channels = {item.get("channel") for item in clocks}
        timestamps = {item.get("timestamp") for item in clocks}
        self.assertGreaterEqual(len(clocks), 4)
        self.assertEqual(
            channels,
            {"vendor", "affiliate_inbox", "global_db", "icsr_awareness"},
        )
        self.assertEqual(
            timestamps,
            {
                "2026-07-19T20:01:00Z",
                "2026-07-20T08:11:00Z",
                "2026-07-21T12:03:00Z",
                "2026-07-20",
            },
        )
        for item in clocks:
            self.assertTrue(item.get("source"))
            self.assertEqual(set(item) & THE_CLOCK_KEYS, set())

    def test_pack_does_not_present_a_single_clock(self) -> None:
        pack = pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
        self.assertEqual(set(pack) & THE_CLOCK_KEYS, set())
        for item in pack["clock_evidence"]:
            self.assertNotEqual(item.get("role"), "the_clock")
            self.assertNotIn(item.get("selected"), {True, "true", "yes"})
