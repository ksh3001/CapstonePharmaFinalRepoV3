from __future__ import annotations

import json
import unittest

from packages.kernel.packs import pv_pack
from tests.helpers import CONTEXT


def _segment_fixture(user: str) -> dict:
    context = dict(CONTEXT)
    context["user"] = user
    return {
        "scenario": {"id": "SEG", "workflow": "pv"},
        "authorized_context": context,
        "evidence": [
            {
                "source": "data/icsr_cases.csv",
                "sha256": "d13496a8a6324d102f1fb0ca373af9dcd1e4fee9f466d6bd14b31bb188a447d2",
                "records": [
                    {
                        "case_id": "PV-1020",
                        "source": "patient_program",
                        "product": "NCB-204",
                        "event": "rash",
                        "country": "DE",
                        "awareness_date": "2026-07-20",
                        "language": "English",
                        "patient_key": "P-SEG",
                    }
                ],
            },
            {
                "source": "data/sensitive_segments.csv",
                    "sha256": "a83a3aef3dbd8ab6af51360fbd74ad44e390c557d4537b466b301f40df0aff26",
                "records": [
                    {"case_id": "PV-1020", "segment": "pregnancy", "access_group": "PV_PREGNANCY"},
                    {"case_id": "PV-1020", "segment": "minor", "access_group": "PV_PAEDIATRIC"},
                ],
            },
            {
                "source": "data/users_entitlements.csv",
                "sha256": "cf155def1a9afc2eb71d54fbf1bf8f52740bb18d095e331aae5f6ac4ec7f0b25",
                "records": [
                    {
                        "user": "safety_physician_1",
                        "role": "safety_physician",
                        "iam_state": "active",
                        "ai_gateway_state": "active",
                    }
                ],
            },
        ],
        "response_contract": "pv_response.schema.json",
    }


class SensitiveSegmentTests(unittest.TestCase):
    def test_unentitled_role_pack_has_no_segment_keys(self) -> None:
        pack = pv_pack(_segment_fixture("participant_test_user"), case_ids=["PV-1020"])
        rendered = json.dumps(pack)
        self.assertNotIn("pregnancy", rendered.casefold())
        self.assertNotIn("pv_pregnancy", rendered.casefold())
        self.assertNotIn("\"minor\"", rendered.casefold())
        self.assertTrue(pack.get("human_review", {}).get("sensitive_segments_withheld"))

    def test_safety_physician_retains_segment_rows(self) -> None:
        pack = pv_pack(_segment_fixture("safety_physician_1"), case_ids=["PV-1020"])
        rendered = json.dumps(pack).casefold()
        self.assertIn("pregnancy", rendered)
        self.assertFalse(pack.get("human_review", {}).get("sensitive_segments_withheld"))
