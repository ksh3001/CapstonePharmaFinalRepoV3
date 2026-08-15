from __future__ import annotations

import json
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class SiteRiskObservationTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_indicators_are_observations_without_scores_or_inspection_calls(self) -> None:
        fixture = load_pub("PUB-15")
        fixture["evidence"] = list(fixture.get("evidence") or []) + [
            {
                "source": "data/site_metrics.csv",
                "records": [
                    {
                        "site_id": "IN-014",
                        "enrolment": "47",
                        "late_source_pct": "31",
                        "digit_preference_flag": "true",
                        "credential_sharing_flag": "true",
                    }
                ],
            }
        ]
        pack = advisory_pack(fixture)
        observations = pack["human_review"]["clinical"]["site_observations"]
        self.assertTrue(any(item.get("site_id") == "IN-014" for item in observations))
        self.assertTrue(any(item.get("site_id") == "DE-008" for item in observations))
        de = next(item for item in observations if item.get("site_id") == "DE-008")
        self.assertIn("not evidence of quality", de.get("statement") or "")
        rendered = json.dumps(pack).casefold()
        self.assertNotIn("site_score", rendered)
        self.assertNotIn("should be inspected", rendered)
        self.assertNotIn("should be audited", rendered)
        self.assertNotIn("non-compliant", rendered)
