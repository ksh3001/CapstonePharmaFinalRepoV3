from __future__ import annotations

import json
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class DeviceSkewTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_wearable_timestamps_are_verbatim_and_unadjusted(self) -> None:
        fixture = load_pub("PUB-15")
        fixture["evidence"] = list(fixture.get("evidence") or []) + [
            {
                "source": "data/wearable_readings.csv",
                "records": [
                    {
                        "subject_id": "S-301-118",
                        "device_id": "WR-11",
                        "timestamp": "2026-03-29 02:15",
                        "timezone": "local_unknown",
                        "heart_rate": "118",
                    },
                    {
                        "subject_id": "S-301-118",
                        "device_id": "WR-11",
                        "timestamp": "2026-03-29T01:20:00Z",
                        "timezone": "UTC",
                        "heart_rate": "121",
                    },
                ],
            }
        ]
        pack = advisory_pack(fixture)
        stamps = pack["human_review"]["clinical"]["device_timestamps"]
        values = {item["timestamp"] for item in stamps}
        self.assertIn("2026-03-29 02:15", values)
        self.assertIn("2026-03-29T01:20:00Z", values)
        self.assertTrue(all(item.get("adjusted") is False for item in stamps))
        skew = pack["human_review"]["clinical"]["device_skew"]
        self.assertTrue(skew)
        self.assertTrue(skew[0]["skew_reported"])
        self.assertFalse(skew[0]["adjusted"])
        rendered = json.dumps(pack)
        self.assertNotIn("adjusted_timestamp", rendered)
