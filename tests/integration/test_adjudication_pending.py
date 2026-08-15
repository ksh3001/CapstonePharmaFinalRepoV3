from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class AdjudicationPendingTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_pending_endpoint_is_excluded_and_not_predicted(self) -> None:
        fixture = load_pub("PUB-15")
        fixture["evidence"] = list(fixture.get("evidence") or []) + [
            {
                "source": "data/endpoint_packets.csv",
                "records": [
                    {
                        "packet_id": "EP-71",
                        "subject_id": "S-301-118",
                        "endpoint": "MRI response",
                        "source_complete": "no",
                        "review_status": "conflict",
                        "queue_entered_at": "2026-07-01",
                        "committee": "imaging_adjudication",
                    }
                ],
            },
            {
                "source": "data/imaging_reviews.csv",
                "records": [
                    {"packet_id": "EP-71", "reviewer": "R1", "conclusion": "responder"},
                    {"packet_id": "EP-71", "reviewer": "R2", "conclusion": "non_responder"},
                ],
            },
        ]
        pack = advisory_pack(fixture)
        pending = pack["human_review"]["clinical"]["pending_adjudication"]
        self.assertTrue(pending)
        self.assertEqual(pending[0]["status"], "pending")
        self.assertEqual(pending[0]["queue_entered_at"], "2026-07-01")
        self.assertEqual(pending[0]["committee"], "imaging_adjudication")
        self.assertFalse(pending[0]["adjudicated"])
        self.assertEqual(pack["human_review"]["clinical"]["adjudicated_count"], 0)
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "adjudication_backlog"]
        self.assertTrue(gaps)
        rendered = str(pack)
        self.assertNotIn("provisional_outcome", rendered)
        self.assertNotIn("predicted_outcome", rendered)
