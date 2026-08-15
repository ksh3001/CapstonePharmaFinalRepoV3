from __future__ import annotations

import copy
import json
import unittest

from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


def _with_purpose(purpose: str) -> dict:
    payload = copy.deepcopy(load_pub("PUB-11"))
    payload["authorized_context"]["purpose"] = purpose
    return payload


class ConsentPerPurposeTests(unittest.TestCase):
    def test_biomarker_withdrawal_blocks_biomarker_and_reports_cached_check(self) -> None:
        blocked = advisory_pack(_with_purpose("biomarker_model"))
        self.assertEqual(blocked["authorization"]["decision"], "deny")
        self.assertIn("biomarker_model", str(blocked["authorization"].get("reason") or ""))
        statements = " ".join(item.get("statement") or "" for item in blocked["findings"]).casefold()
        self.assertIn("cached_active", statements)
        self.assertIn("pe-9", statements)
        self.assertEqual(blocked["evidence"], [])

    def test_trial_purpose_remains_available(self) -> None:
        allowed = advisory_pack(_with_purpose("trial"))
        self.assertEqual(allowed["authorization"]["decision"], "allow")
        statements = " ".join(item.get("statement") or "" for item in allowed["findings"]).casefold()
        self.assertIn("cached_active", statements)

    def test_withdrawn_subject_is_withheld_and_reported(self) -> None:
        pack = advisory_pack(_with_purpose("biomarker_model"))
        rendered = json.dumps(pack).casefold()
        self.assertIn("withheld", rendered)
        self.assertNotIn("ultra_rare", rendered)
