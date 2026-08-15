from __future__ import annotations

import json
import unittest

from packages.contracts.deny import assert_clean, grade
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class ProtocolApplicabilityTests(unittest.TestCase):
    def test_site_approved_version_governs_not_global_currency(self) -> None:
        pack = advisory_pack(load_pub("PUB-15"))
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertEqual(pack["workflow"], "clinical")
        rows = pack["human_review"]["clinical"]["applicability"]
        subject = next(item for item in rows if item.get("subject_id") == "S-301-044")
        self.assertEqual(subject["governing_version"], "4.1")
        self.assertEqual(subject["governing_source"], "data/site_approvals.csv")
        self.assertEqual(subject["globally_current_version"], "5.0")
        self.assertIn("not locally approved", subject["statement"])
        risks = pack["human_review"]["clinical"]["protocol_risks"]
        self.assertTrue(any(item.get("version") == "3.2" for item in risks))
        self.assertTrue(any(item.get("status") == "obsolete_but_site_cached" for item in risks))
        self.assertEqual(grade(pack), [])
        assert_clean(pack)

    def test_pending_amendment_is_a_gap_and_five_does_not_apply(self) -> None:
        pack = advisory_pack(load_pub("PUB-15"))
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "pending_amendment"]
        self.assertTrue(gaps)
        self.assertEqual(gaps[0]["subject_id"], "IN-014")
        rendered = json.dumps(pack).casefold()
        self.assertNotIn("5.0 applies", rendered)
        self.assertNotIn("5.0 applies at", rendered)
