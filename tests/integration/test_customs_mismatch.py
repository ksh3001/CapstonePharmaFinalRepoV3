from __future__ import annotations

import unittest

from packages.kernel.packs import supply_pack
from tests.helpers import fixture_with


class CustomsMismatchTests(unittest.TestCase):
    def test_invoice_and_licence_descriptions_are_retained(self) -> None:
        fixture = fixture_with(
            [
                {
                    "source": "data/trade_documents.csv",
                    "records": [
                        {
                            "shipment_id": "SH-902",
                            "document": "invoice",
                            "description": "sterile research samples",
                        },
                        {
                            "shipment_id": "SH-902",
                            "document": "import_licence",
                            "description": "commercial sterile injectable",
                        },
                    ],
                }
            ],
            scenario_id="SYN-CUSTOMS",
            workflow="supply",
        )
        pack = supply_pack(fixture, event_id="SH-902")
        findings = pack.get("human_review", {}).get("security_findings") or []
        mismatch = [item for item in findings if item.get("kind") == "customs_mismatch"]
        self.assertTrue(mismatch)
        statement = mismatch[0]["statement"]
        self.assertIn("description", statement)
        self.assertIn("sterile research samples", statement)
        self.assertIn("commercial sterile injectable", statement)
        rendered = str(pack).casefold()
        self.assertNotIn("compliant", rendered)
        self.assertNotIn("clearance", rendered)
        self.assertNotIn("amend", rendered)
