from __future__ import annotations

import unittest

from packages.kernel.packs import supply_pack
from tests.helpers import fixture_with


class SubstituteQualificationTests(unittest.TestCase):
    def test_unqualified_substitute_is_described_not_counted(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/supplier_risks.csv",
                    "records": [
                        {
                            "supplier": "EXCIP-ONE",
                            "material": "Polysorbate-X",
                            "risk": "contamination",
                            "recovery_weeks": "8",
                            "alternate_qualified": "no",
                        }
                    ],
                },
                {
                    "source": "data/demand_forecast.csv",
                    "records": [
                        {
                            "channel": "commercial_EU",
                            "product": "NCB-204",
                            "units_8w": "5200",
                        }
                    ],
                },
            ],
            scenario_id="SYN-SUB",
            workflow="supply",
        )
        pack = supply_pack(fixture, event_id="NCB-204-shortage")
        substitutes = [item for item in pack["options"] if str(item.get("option_id")).startswith("OPT-SUB-")]
        self.assertTrue(substitutes)
        option = substitutes[0]
        self.assertEqual(option["qualification_status"], "unqualified")
        self.assertTrue(option["change_control_required"])
        self.assertTrue(option["regulatory_variation_required"])
        self.assertFalse(option["presented_as_available_supply"])
        self.assertEqual(option["status"], "draft")
        rendered = str(pack).casefold()
        self.assertNotIn("may be used", rendered)
        for demand in pack["options"]:
            for position in demand.get("released_positions") or []:
                self.assertNotEqual(str(position.get("material") or ""), "Polysorbate-X")
