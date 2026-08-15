from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with, load_pub


class ManualAssignmentProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_complete_manual_assignment_is_marked_and_not_overwritten(self) -> None:
        fixture = load_pub("PUB-10")
        fixture["evidence"] = list(fixture.get("evidence") or []) + [
            {
                "source": "data/continuity_requirements.csv",
                "records": [
                    {
                        "assignment_id": "MA-77",
                        "assigned_by": "qa_lead_4",
                        "assigned_at": "2026-07-20T10:00:00Z",
                        "authority": "contingency-SOP-12",
                        "procedure": "docs/runbooks/pv_intake.md",
                        "manual_assignment": "yes",
                    }
                ],
            },
            {
                "source": "data/continuity_requirements.csv",
                "records": [
                    {
                        "assignment_id": "MA-77",
                        "assigned_by": "irt_service",
                        "assigned_at": "2026-07-21T08:00:00Z",
                        "system_recovered": "yes",
                    }
                ],
            },
        ]
        pack = advisory_pack(fixture)
        facts = next(
            item["facts"]
            for item in pack["evidence"]
            if str(item["facts"].get("manual_assignment") or "").casefold() == "yes"
        )
        self.assertEqual(facts["assigned_by"], "qa_lead_4")
        self.assertEqual(facts["assigned_at"], "2026-07-20T10:00:00Z")
        self.assertEqual(facts["authority"], "contingency-SOP-12")
        self.assertEqual(facts["procedure"], "docs/runbooks/pv_intake.md")
        contradictions = [item for item in pack["contradictions"] if item.get("topic") == "outage_assignment"]
        self.assertTrue(contradictions)
        statement = contradictions[0]["statement"].casefold()
        self.assertIn("both retained", statement)
        self.assertTrue(contradictions[0].get("manual"))
        self.assertTrue(contradictions[0].get("system"))

    def test_incomplete_manual_assignment_is_a_gap(self) -> None:
        payload = fixture_with(
            [
                {
                    "source": "data/continuity_requirements.csv",
                    "records": [
                        {
                            "assignment_id": "MA-incomplete",
                            "assigned_by": "",
                            "assigned_at": "2026-07-20T10:00:00Z",
                            "authority": "contingency-SOP-12",
                            "procedure": "",
                            "manual_assignment": "yes",
                        }
                    ],
                }
            ],
            scenario_id="MA-GAP",
            workflow="reliability",
        )
        pack = advisory_pack(payload)
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "manual_assignment_provenance"]
        self.assertTrue(gaps)
        self.assertIn("assigned_by", gaps[0]["missing_fields"])
        self.assertIn("procedure", gaps[0]["missing_fields"])
        self.assertIn("not assumed", gaps[0]["statement"].casefold())
        facts = pack["evidence"][0]["facts"]
        self.assertEqual(facts.get("assigned_by"), "")
        self.assertEqual(facts.get("procedure"), "")
