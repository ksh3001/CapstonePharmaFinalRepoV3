from __future__ import annotations

import unittest

from packages.ontology.temporal import back_entry, preserve_time


class TemporalPrecisionTests(unittest.TestCase):
    def test_date_only_is_not_widened(self) -> None:
        point = preserve_time("2026-07-20", basis="event_time")
        self.assertEqual(point.value, "2026-07-20")
        self.assertEqual(point.precision, "date")
        self.assertFalse(point.timezone_known)
        self.assertNotIn("T", point.value)
        self.assertNotIn("Z", point.value)

    def test_missing_timezone_stays_missing(self) -> None:
        point = preserve_time("2026-07-10T08:00:00", basis="recorded_at")
        self.assertEqual(point.value, "2026-07-10T08:00:00")
        self.assertFalse(point.timezone_known)

    def test_any_back_entry_difference_is_flagged(self) -> None:
        flag = back_entry("2026-07-10", "2026-07-12")
        self.assertTrue(flag.flagged)
        self.assertEqual(flag.magnitude, "2d")
        self.assertEqual(flag.event_time, "2026-07-10")
        self.assertEqual(flag.recorded_at, "2026-07-12")

    def test_date_only_and_timestamp_are_preserved_under_e2b(self) -> None:
        from packages.kernel.packs import advisory_pack
        from tests.helpers import fixture_with

        fixture = fixture_with(
            [
                {
                    "source": "data/api_contract_versions.csv",
                    "records": [
                        {
                            "api": "Safety ICSR",
                            "version": "E2B_R3",
                            "date_semantics": "precision variable",
                        }
                    ],
                },
                {
                    "source": "data/icsr_cases.csv",
                    "records": [
                        {
                            "case_id": "PV-DATE",
                            "contract_version": "E2B_R3",
                            "result_id": "PV-DATE",
                            "date": "2026-07-20",
                        },
                        {
                            "case_id": "PV-TS",
                            "contract_version": "E2B_R3",
                            "result_id": "PV-TS",
                            "date": "2026-07-20T08:15:00Z",
                        },
                    ],
                },
            ],
            scenario_id="SYN-E2B",
            workflow="integration",
        )
        pack = advisory_pack(fixture)
        dates = {item["record_id"]: item for item in pack["human_review"]["interface_reconciliation"]["dates"]}
        self.assertEqual(dates["PV-DATE"]["value"], "2026-07-20")
        self.assertEqual(dates["PV-DATE"]["precision"], "date")
        self.assertEqual(dates["PV-TS"]["value"], "2026-07-20T08:15:00Z")
        self.assertIn(dates["PV-TS"]["precision"], {"datetime_tz", "datetime"})

