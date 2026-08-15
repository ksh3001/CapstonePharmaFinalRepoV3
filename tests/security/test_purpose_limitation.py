from __future__ import annotations

import copy
import json
import unittest

from packages.kernel.packs import advisory_pack, pv_pack
from tests.helpers import load_pub


def _with_purpose(name: str, purpose: str) -> dict:
    payload = copy.deepcopy(load_pub(name))
    payload["authorized_context"]["purpose"] = purpose
    return payload


class PurposeLimitationTests(unittest.TestCase):
    def test_unregistered_purpose_is_denied_and_named(self) -> None:
        pack = advisory_pack(_with_purpose("PUB-11", "commercial_secondary"))
        self.assertEqual(pack["authorization"]["decision"], "deny")
        reason = str(pack["authorization"].get("reason") or "")
        self.assertIn("commercial_secondary", reason)
        self.assertIn("unregistered", reason)
        self.assertEqual(pack["evidence"], [])
        self.assertEqual(pack["execution_status"], "not_executed")

    def test_pv_purpose_without_consent_loads_no_case_content(self) -> None:
        pack = pv_pack(_with_purpose("PUB-04", "biomarker_model"), case_ids=["PV-1001"])
        self.assertEqual(pack["authorization"]["decision"], "deny")
        self.assertEqual(pack["source_facts"], [])
        self.assertEqual(pack["clock_evidence"], [])
        self.assertEqual(pack["terminology"], [])
        rendered = json.dumps(pack)
        self.assertNotIn("P-7X", rendered)
        self.assertNotIn("anaphylaxis", rendered.casefold())
