from __future__ import annotations

import unittest

from packages.config.paths import repo_root
from packages.domain.continuity import MANDATORY_WORKFLOWS, RUNBOOK_DIR
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with, load_pub


class RunbooksExistTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_each_mandatory_workflow_runbook_exists_and_is_referenced(self) -> None:
        pack = advisory_pack(load_pub("PUB-10"))
        workflows = {item["workflow"]: item for item in pack["human_review"]["continuity"]["workflows"]}
        for name in MANDATORY_WORKFLOWS:
            path = repo_root() / RUNBOOK_DIR / f"{name}.md"
            self.assertTrue(path.is_file(), name)
            self.assertEqual(workflows[name]["runbook"], f"{RUNBOOK_DIR}/{name}.md")
            self.assertFalse(
                any(
                    item.get("gap_type") == "missing_runbook" and item.get("subject_id") == name
                    for item in pack["gaps"]
                )
            )

    def test_missing_runbook_is_a_gap(self) -> None:
        payload = fixture_with(
            [
                {
                    "source": "data/continuity_requirements.csv",
                    "records": [
                        {
                            "workflow": "orphan_flow",
                            "max_ai_outage_days": "1",
                            "manual_runbook": "required",
                            "max_ai_outage_hours": "1",
                        }
                    ],
                }
            ],
            scenario_id="RB-MISS",
            workflow="reliability",
        )
        pack = advisory_pack(payload)
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "missing_runbook"]
        self.assertTrue(gaps)
        self.assertEqual(gaps[0]["subject_id"], "orphan_flow")
