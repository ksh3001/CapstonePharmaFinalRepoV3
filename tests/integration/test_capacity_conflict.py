from __future__ import annotations

import unittest

from packages.kernel.packs import supply_pack
from tests.helpers import fixture_with


class CapacityConflictTests(unittest.TestCase):
    def test_double_promised_capacity_is_not_treated_as_available(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/cmo_capacity.csv",
                    "records": [
                        {
                            "cmo": "CMO-IE",
                            "window": "2026-W34",
                            "capacity_batches": "2",
                            "promised_NTG": "2",
                            "promised_other_sponsor": "1",
                        }
                    ],
                },
                {
                    "source": "data/demand_forecast.csv",
                    "records": [
                        {
                            "channel": "clinical_trial",
                            "product": "NCB-204",
                            "units_8w": "900",
                        }
                    ],
                },
            ],
            scenario_id="SYN-CMO",
            workflow="supply",
        )
        pack = supply_pack(fixture, event_id="CMO-IE")
        findings = pack.get("human_review", {}).get("security_findings") or []
        conflicts = [item for item in findings if item.get("kind") == "capacity_conflict"]
        self.assertTrue(conflicts)
        statement = conflicts[0]["statement"]
        self.assertIn("2", statement)
        self.assertIn("1", statement)
        self.assertTrue(any(item.get("contested") for item in pack["constraints"]))
        for option in pack["options"]:
            self.assertNotEqual(option.get("available_capacity"), "2")
            self.assertFalse(option.get("treats_contested_as_available"))
        rendered = str(pack).casefold()
        self.assertNotIn("allocate stock", rendered)
