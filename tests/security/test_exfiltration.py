from __future__ import annotations

import json
import unittest

from packages.kernel.packs import pv_pack
from tests.helpers import fixture_with, CONTEXT


class ExfiltrationTests(unittest.TestCase):
    def test_unapproved_export_is_denied_without_payload(self) -> None:
        payload = fixture_with(
            [
                {
                    "source": "data/data_exports.csv",
                    "sha256": "placeholder",
                    "records": [
                        {
                            "export_id": "EX-77",
                            "dataset": "NCB204 trial biomarker",
                            "from_region": "EU",
                            "to_region": "US",
                            "purpose": "global model training",
                            "approved": "no",
                        }
                    ],
                },
                {
                    "source": "data/icsr_cases.csv",
                    "sha256": "d13496a8a6324d102f1fb0ca373af9dcd1e4fee9f466d6bd14b31bb188a447d2",
                    "records": [
                        {
                            "case_id": "PV-1001",
                            "product": "NCB-204",
                            "event": "anaphylaxis",
                            "language": "German",
                            "patient_key": "P-7X",
                        }
                    ],
                },
            ],
            scenario_id="EXFIL",
            workflow="pv",
        )
        pack = pv_pack(payload, case_ids=["PV-1001"])
        self.assertEqual(pack["authorization"]["decision"], "deny")
        self.assertEqual(pack["source_facts"], [])
        rendered = json.dumps(pack)
        self.assertNotIn("P-7X", rendered)
        self.assertNotIn("anaphylaxis", rendered.casefold())
