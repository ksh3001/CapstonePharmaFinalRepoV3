from __future__ import annotations

import json
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class BlindingProtectionTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_allocation_and_kit_are_absent_and_combination_is_withheld(self) -> None:
        fixture = load_pub("PUB-15")
        fixture["evidence"] = list(fixture.get("evidence") or []) + [
            {
                "source": "data/randomization_events.csv",
                "records": [
                    {
                        "event_id": "IRT-9001",
                        "subject_id": "S-301-118",
                        "kit": "K-7701",
                        "method": "manual_downtime_log",
                        "time": "2026-07-24T14:12:00+02:00",
                    }
                ],
            }
        ]
        pack = advisory_pack(fixture)
        rendered = json.dumps(pack)
        self.assertNotIn("K-7701", rendered)
        self.assertNotIn('"kit"', rendered)
        self.assertNotIn("allocation", rendered.casefold())
        unblinding = pack["human_review"]["clinical"].get("unblinding") or pack["human_review"].get("unblinding")
        self.assertTrue(unblinding.get("combination_withheld"))
        self.assertEqual(unblinding.get("routed_to"), "unblinding_authority")
        findings = [item for item in pack["findings"] if "unblind" in str(item.get("statement") or "").casefold() or item.get("finding_id") == "F-UNBLIND-COMBINATION"]
        self.assertTrue(findings)
        self.assertNotIn("K-7701", findings[0]["statement"])
