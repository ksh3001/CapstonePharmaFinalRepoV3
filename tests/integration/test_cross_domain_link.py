from __future__ import annotations

import unittest

from packages.config.matching import LINKAGE_WINDOW_DAYS
from packages.kernel.packs import pv_pack
from tests.helpers import fixture_with


def _triple(complaint_date: str, batch_date: str, icsr_date: str) -> list[dict]:
    return [
        {
            "source": "data/product_complaints.csv",
            "records": [
                {
                    "complaint_id": "PC-701",
                    "product": "NCS-310",
                    "lot": "NCS310-S26033",
                    "issue": "visible particles",
                    "date": complaint_date,
                }
            ],
        },
        {
            "source": "data/batches.csv",
            "records": [
                {
                    "batch_id": "NCS310-S26033",
                    "product_id": "NCS-310",
                    "manufacture_date": batch_date,
                }
            ],
        },
        {
            "source": "data/icsr_cases.csv",
            "records": [
                {
                    "case_id": "PV-1001",
                    "source": "patient_program",
                    "product": "NCS-310",
                    "lot": "NCS310-S26033",
                    "awareness_date": icsr_date,
                    "language": "English",
                }
            ],
        },
    ]


class CrossDomainLinkTests(unittest.TestCase):
    def test_shared_lot_within_window_is_unconfirmed_link(self) -> None:
        self.assertEqual(LINKAGE_WINDOW_DAYS, 30)
        fixture = fixture_with(
            _triple("2026-07-22", "2026-07-20", "2026-07-25"),
            scenario_id="SYN-LINK",
            workflow="pv",
        )
        pack = pv_pack(fixture, case_ids=["PV-1001"])
        links = pack["human_review"]["unconfirmed_links"]
        self.assertTrue(links)
        self.assertTrue(all(item.get("kind") == "unconfirmed_link" for item in links))
        self.assertTrue(all(item.get("shared_identifier") == "NCS310-S26033" for item in links))
        self.assertTrue(all(int(item["time_distance_days"]) <= 30 for item in links))
        rendered = str(pack).casefold()
        self.assertNotIn("causal relationship", rendered)
        self.assertNotIn("quality relationship established", rendered)

    def test_shared_lot_outside_window_is_absent(self) -> None:
        fixture = fixture_with(
            _triple("2026-07-22", "2026-07-20", "2026-01-01"),
            scenario_id="SYN-LINK-FAR",
            workflow="pv",
        )
        pack = pv_pack(fixture, case_ids=["PV-1001"])
        links = pack.get("human_review", {}).get("unconfirmed_links") or []
        icsr_links = [
            item
            for item in links
            if "PV-1001" in {item["left"]["record_id"], item["right"]["record_id"]}
        ]
        self.assertEqual(icsr_links, [])
