from __future__ import annotations

import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with


class ChangeControlBypassTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_missing_approval_is_an_integrity_finding(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/product_complaints.csv",
                    "records": [
                        {
                            "record_id": "CC-1",
                            "change_id": "CC-1",
                            "change_date": "2026-07-01",
                            "approval_ref": "missing",
                        }
                    ],
                }
            ],
            scenario_id="SYN-CC-MISSING",
            workflow="security",
        )
        pack = advisory_pack(fixture)
        validate(pack, resolve_contract("advisory_nonexecuting"))
        findings = [item for item in pack["findings"] if str(item["finding_id"]).startswith("F-CC-")]
        self.assertTrue(findings)
        self.assertIn("outside change control", findings[0]["statement"].casefold())
        self.assertEqual(pack["evidence"][0]["facts"].get("trust_status"), "reduced_integrity")

    def test_retrospective_approval_does_not_clear_the_finding(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/product_complaints.csv",
                    "records": [
                        {
                            "record_id": "CC-2",
                            "change_id": "CC-2",
                            "change_date": "2026-07-01",
                            "approval_date": "2026-07-20",
                            "approval_ref": "CC-RETRO-1",
                        }
                    ],
                }
            ],
            scenario_id="SYN-CC-RETRO",
            workflow="security",
        )
        pack = advisory_pack(fixture)
        validate(pack, resolve_contract("advisory_nonexecuting"))
        findings = [item for item in pack["findings"] if str(item["finding_id"]).startswith("F-CC-")]
        self.assertTrue(findings)
        self.assertIn("retrospective", findings[0]["statement"].casefold())
        self.assertIn("does not clear", findings[0]["statement"].casefold())
        self.assertEqual(pack["evidence"][0]["facts"].get("trust_status"), "reduced_integrity")
        reset_replay()
        again = advisory_pack(fixture)
        self.assertTrue(any(str(item["finding_id"]).startswith("F-CC-") for item in again["findings"]))
