from __future__ import annotations

import json
import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.packs import batch_pack
from tests.helpers import fixture_with


class CleaningValidationBoundaryTests(unittest.TestCase):
    def test_beyond_boundary_raises_gap_without_adequacy_claim(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/batches.csv",
                    "records": [
                        {
                            "batch_id": "HP-NEW-C882",
                            "product_id": "HP-NEW",
                            "site": "NTG-IN",
                            "status": "pending_review",
                            "manufacture_date": "2026-08-04",
                        }
                    ],
                },
                {
                    "source": "data/cleaning_validation.csv",
                    "records": [
                        {
                            "equipment": "BLEND-04",
                            "previous_product": "NCX-101",
                            "next_product": "HP-NEW",
                            "validation_scope": "NCX only",
                            "status": "gap",
                        }
                    ],
                },
                {
                    "source": "data/production_schedule.csv",
                    "records": [
                        {
                            "equipment": "BLEND-04",
                            "campaign": "C-882",
                            "product_sequence": "NCX-101>HP-NEW>NCX-101",
                            "start": "2026-08-04",
                        }
                    ],
                },
            ],
            scenario_id="SYN-CLEAN",
        )
        pack = batch_pack(fixture, batch_id="HP-NEW-C882")
        validate(pack, resolve_contract("batch_response.schema.json"))
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "cleaning_boundary"]
        self.assertTrue(gaps, pack["gaps"])
        self.assertEqual(gaps[0].get("boundary"), "NCX only")
        self.assertEqual(gaps[0].get("preceding_product"), "NCX-101")
        self.assertNotEqual(pack["readiness_state"], "ready_for_authorized_review")
        rendered = json.dumps(pack).lower()
        self.assertNotIn("cleaning was adequate", rendered)
        self.assertNotIn("cleaning was validated", rendered)
