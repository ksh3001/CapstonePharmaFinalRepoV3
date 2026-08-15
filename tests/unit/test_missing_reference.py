from __future__ import annotations

import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with


class MissingReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_absent_referenced_document_is_a_named_gap(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/knowledge_catalog.csv",
                    "records": [
                        {
                            "doc_id": "K-006",
                            "file": "BATCH_RELEASE_EVIDENCE_POLICY.md",
                            "authority": "NovaCura Global Policy",
                            "effective": "2026-06-01",
                            "status": "approved",
                            "references": "K-MISSING",
                        }
                    ],
                }
            ],
            scenario_id="SYN-MISSING-REF",
            workflow="security",
        )
        pack = advisory_pack(fixture)
        validate(pack, resolve_contract("advisory_nonexecuting"))
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "referenced_missing"]
        self.assertTrue(gaps)
        self.assertEqual(gaps[0]["subject_id"], "K-MISSING")
        self.assertIn("K-MISSING", gaps[0].get("statement", ""))
