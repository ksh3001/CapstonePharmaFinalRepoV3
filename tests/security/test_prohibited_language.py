from __future__ import annotations

import json
import unittest
from pathlib import Path

from packages.contracts.deny import DenyListError, assert_baseline, assert_clean, grade
from packages.kernel.packs import advisory_pack, batch_pack, pv_pack, supply_pack
from tests.helpers import load_pub


class ProhibitedLanguageTests(unittest.TestCase):
    def test_nested_approved_for_release_is_rejected(self) -> None:
        pack = {
            "execution_status": "not_executed",
            "evidence": [],
            "human_review": {"notes": {"inner": "Lot is approved for release pending QA."}},
        }
        hits = grade(pack)
        self.assertTrue(any("approved for release" in item for item in hits), hits)
        with self.assertRaises(DenyListError):
            assert_clean(pack)

    def test_clean_pack_passes(self) -> None:
        pack = {
            "execution_status": "not_executed",
            "evidence": [],
            "findings": [{"finding_id": "F-1", "statement": "Hold remains in force.", "evidence_refs": []}],
        }
        self.assertEqual(grade(pack), [])

    def test_pub01_batch_pack_is_clean(self) -> None:
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        self.assertEqual(grade(pack), [])
        assert_clean(pack)

    def test_pv_packs_have_no_decision_conclusions(self) -> None:
        packs = [
            pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"]),
            pv_pack(load_pub("PUB-05"), case_ids=["SM-77"]),
            pv_pack(load_pub("PUB-06"), case_ids=["NCB-204"]),
        ]
        for pack in packs:
            with self.subTest(scenario=pack.get("request_id")):
                self.assertEqual(grade(pack), [])
                assert_clean(pack)

    def test_supply_packs_have_no_execution_verbs(self) -> None:
        packs = [
            supply_pack(load_pub("PUB-07"), event_id="NCB-204-shortage"),
            supply_pack(load_pub("PUB-08"), event_id="SH-901"),
        ]
        for pack in packs:
            with self.subTest(scenario=pack.get("request_id")):
                self.assertEqual(grade(pack), [])
                assert_clean(pack)

    def test_clinical_and_regulatory_packs_have_no_decision_conclusions(self) -> None:
        from tests.unit.test_identity_conflict import regulatory_fixture

        packs = [
            advisory_pack(load_pub("PUB-15")),
            advisory_pack(regulatory_fixture()),
        ]
        for pack in packs:
            with self.subTest(workflow=pack.get("workflow")):
                self.assertEqual(grade(pack), [])
                assert_clean(pack)
                rendered = json.dumps(pack).casefold()
                self.assertNotIn("patient is eligible", rendered)
                self.assertNotIn("patient is ineligible", rendered)
                self.assertNotIn("screen failure", rendered)
                self.assertNotIn("commitment was met", rendered)
                self.assertNotIn("submission was accepted", rendered)

    def test_shrinking_deny_list_fails_baseline(self) -> None:
        from packages.contracts import deny

        original = Path(deny.DENY_LIST_PATH).read_text(encoding="utf-8")
        payload = json.loads(original)
        payload["phrases"] = [item for item in payload["phrases"] if item != "approved for release"]
        Path(deny.DENY_LIST_PATH).write_text(json.dumps(payload), encoding="utf-8")
        try:
            with self.assertRaises(DenyListError):
                assert_baseline()
        finally:
            Path(deny.DENY_LIST_PATH).write_text(original, encoding="utf-8")
