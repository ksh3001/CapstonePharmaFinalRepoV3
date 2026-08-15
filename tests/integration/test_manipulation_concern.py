from __future__ import annotations

import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with


def _fixture(rows: list[dict[str, str]]) -> dict:
    return fixture_with(
        [{"source": "data/lab_results.csv", "records": rows}],
        scenario_id="SYN-MANIP",
        workflow="security",
    )


class ManipulationConcernTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_manipulation_finding_is_not_cleared_by_a_later_record_or_rerun(self) -> None:
        first = {
            "record_id": "IMG-1",
            "image_id": "IMG-1",
            "manipulation": "recropped",
        }
        later = {
            "record_id": "IMG-1-CLEAR",
            "image_id": "IMG-1",
            "manipulation": "cleared",
        }
        pack = advisory_pack(_fixture([first, later]))
        validate(pack, resolve_contract("advisory_nonexecuting"))
        findings = [item for item in pack["findings"] if str(item["finding_id"]).startswith("F-MANIP-")]
        self.assertTrue(findings)
        self.assertIn("reduced_integrity", findings[0]["statement"])
        self.assertEqual(pack["evidence"][0]["facts"].get("trust_status"), "reduced_integrity")
        reset_replay()
        again = advisory_pack(_fixture([first, later]))
        again_findings = [item for item in again["findings"] if str(item["finding_id"]).startswith("F-MANIP-")]
        self.assertTrue(again_findings)
        self.assertEqual(again["evidence"][0]["facts"].get("trust_status"), "reduced_integrity")
