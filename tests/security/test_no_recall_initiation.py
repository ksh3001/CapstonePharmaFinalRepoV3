from __future__ import annotations

import unittest

from packages.contracts.deny import assert_clean, grade
from packages.kernel.packs import supply_pack
from tests.helpers import fixture_with


class NoRecallInitiationTests(unittest.TestCase):
    def test_counterfeit_indicators_escalate_without_recall_language(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/image_forensics.csv",
                    "records": [
                        {
                            "study_id": "PC-88",
                            "panel": "Figure_6B",
                            "similarity_to": "Figure_4A",
                            "similarity_score": "0.97",
                            "metadata_note": "same acquisition timestamp",
                        }
                    ],
                }
            ],
            scenario_id="SYN-RECALL",
            workflow="supply",
        )
        pack = supply_pack(fixture, event_id="PC-88")
        findings = pack.get("human_review", {}).get("security_findings") or []
        self.assertTrue(any(item.get("kind") == "counterfeit_suspicion" for item in findings), findings)
        self.assertTrue(any(item.get("escalation") == "quality_reviewer" for item in findings), findings)
        rendered = str(pack).casefold()
        self.assertNotIn("initiate recall", rendered)
        self.assertNotIn("recall initiated", rendered)
        self.assertEqual(grade(pack), [])
        assert_clean(pack)
