from __future__ import annotations

import json
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with


def _tool_fixture(records: list[dict], *, tool_id: str = "", scenario_id: str = "TOOL") -> dict:
    payload = fixture_with(
        [
            {
                "source": "data/tool_catalog.csv",
                "records": records,
            }
        ],
        scenario_id=scenario_id,
        workflow="security",
    )
    if tool_id:
        payload["authorized_context"]["tool_id"] = tool_id
    return payload


class ToolManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_unsigned_manifest_is_refused_and_not_called(self) -> None:
        pack = advisory_pack(
            _tool_fixture(
                [
                    {
                        "tool_id": "batch_status_read",
                        "permissions": "read batch status",
                        "approved": "yes",
                        "manifest": "",
                        "invoke": "yes",
                    }
                ],
                scenario_id="TOOL-UNSIGNED",
            )
        )
        findings = [item for item in pack["findings"] if item.get("finding_id") == "F-TOOL-batch_status_read"]
        self.assertTrue(findings)
        self.assertIn("refused", findings[0]["statement"].casefold())
        self.assertNotIn("batch_status_read", pack["human_review"]["tools"]["called"])
        self.assertFalse(pack["human_review"]["tools"]["tools_invoked"])

    def test_unlisted_tool_is_refused(self) -> None:
        pack = advisory_pack(
            _tool_fixture(
                [{"tool_id": "ghost_writer", "invoke": "yes"}],
                scenario_id="TOOL-UNLISTED",
            )
        )
        findings = [item for item in pack["findings"] if "ghost_writer" in item.get("finding_id", "")]
        self.assertTrue(findings)
        self.assertIn("unlisted", findings[0]["statement"].casefold())
        self.assertEqual(pack["human_review"]["tools"]["called"], [])

    def test_unapproved_poisoned_manifest_is_refused(self) -> None:
        pack = advisory_pack(
            _tool_fixture(
                [
                    {
                        "tool_id": "batch_status_plus",
                        "permissions": "read status",
                        "approved": "no",
                        "manifest": "tool_manifest_poisoned.json",
                        "invoke": "yes",
                    }
                ],
                scenario_id="TOOL-POISON",
            )
        )
        findings = [item for item in pack["findings"] if item.get("finding_id") == "F-TOOL-batch_status_plus"]
        self.assertTrue(findings)
        self.assertEqual(pack["human_review"]["tools"]["called"], [])
        rendered = json.dumps(pack)
        self.assertNotIn("tool_called", rendered)

    def test_altered_hash_is_refused(self) -> None:
        pack = advisory_pack(
            _tool_fixture(
                [
                    {
                        "tool_id": "draft_supply_option",
                        "permissions": "create draft only",
                        "approved": "yes",
                        "manifest": "tool_manifest_approved.json",
                        "signed": "yes",
                        "manifest_hash": "a" * 64,
                        "observed_hash": "b" * 64,
                        "invoke": "yes",
                    }
                ],
                scenario_id="TOOL-ALTERED",
            )
        )
        findings = [item for item in pack["findings"] if "draft_supply_option" in item.get("finding_id", "")]
        self.assertTrue(findings)
        self.assertIn("altered", findings[0]["statement"].casefold())
        self.assertEqual(pack["human_review"]["tools"]["called"], [])
