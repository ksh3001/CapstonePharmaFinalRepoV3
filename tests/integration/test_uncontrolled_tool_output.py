from __future__ import annotations

import json
import unittest

from packages.domain.graph_findings import uncontrolled_calculation


class UncontrolledToolOutputTests(unittest.TestCase):
    def test_unvalidated_spreadsheet_is_not_authority(self) -> None:
        record, abstention = uncontrolled_calculation(
            value="99.9",
            tool="Dissolution_Acceptance_v7.xlsm",
            verified="no",
        )
        self.assertIsNotNone(abstention)
        assert abstention is not None
        self.assertEqual(abstention.reason_code, "uncontrolled_calculation")
        self.assertEqual(record["tool"], "Dissolution_Acceptance_v7.xlsm")
        self.assertTrue(record["uncontrolled_calculation"])
        self.assertFalse(record["authority"])
        rendered = json.dumps({"calculation": record, "abstentions": [abstention.as_dict()]})
        self.assertIn("Dissolution_Acceptance_v7.xlsm", rendered)
        self.assertNotIn("approved for release", rendered.lower())

    def test_verified_tool_may_be_cited(self) -> None:
        record, abstention = uncontrolled_calculation(
            value="98.0",
            tool="validated_lmis.xlsx",
            verified="yes",
        )
        self.assertIsNone(abstention)
        self.assertTrue(record["authority"])
        self.assertFalse(record["uncontrolled_calculation"])
