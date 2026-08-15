from __future__ import annotations

import json
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub

FORBIDDEN = ("reconnection", "restoration", "payment", "environment-clean", "environment clean")


class IsolatedSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_isolated_source_is_stale_and_not_authority(self) -> None:
        fixture = load_pub("PUB-10")
        fixture["evidence"] = list(fixture.get("evidence") or []) + [
            {
                "source": "data/model_endpoints.csv",
                "records": [
                    {
                        "system": "MES-historian",
                        "last_known_good": "2026-07-18T04:00:00Z",
                        "isolation_event": "OT-SEG-069",
                        "incident_window": "yes",
                    }
                ],
            }
        ]
        pack = advisory_pack(fixture)
        facts = pack["human_review"]["continuity"]["isolated_facts"]
        self.assertTrue(facts)
        row = facts[0]
        self.assertEqual(row["last_known_good"], "2026-07-18T04:00:00Z")
        self.assertEqual(row["isolation_event"], "OT-SEG-069")
        self.assertFalse(row["current"])
        self.assertEqual(row["integrity"], "integrity_unconfirmed")
        self.assertFalse(row["authority"])
        for item in pack["human_review"]["continuity"]["workflows"]:
            self.assertEqual(item["path"], "manual")
        rendered = json.dumps(pack).casefold()
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, rendered, phrase)
