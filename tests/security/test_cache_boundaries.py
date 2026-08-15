from __future__ import annotations

import json
import unittest

from packages.cache import CACHE, ProtectedCacheError
from packages.kernel.packs import advisory_pack, pv_pack
from tests.helpers import load_pub


class CacheBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        CACHE.clear()

    def test_protected_namespaces_cannot_be_written(self) -> None:
        for key in (
            "authz:user",
            "consent:C-044",
            "residency:EU",
            "hold:LH-44",
            "entitlement:role",
            "checkpoint:freshness",
        ):
            with self.subTest(key=key):
                with self.assertRaises(ProtectedCacheError):
                    CACHE.put(key, "cached")

    def test_full_run_leaves_no_protected_keys(self) -> None:
        pv_pack(load_pub("PUB-04"), case_ids=["PV-1001"])
        advisory_pack(load_pub("PUB-11"))
        rendered = json.dumps(CACHE.keys())
        for token in ("authz", "consent", "residency", "hold", "entitlement"):
            self.assertNotIn(token, rendered)
        self.assertEqual(CACHE.keys(), [])

    def test_hold_check_is_not_cached(self) -> None:
        from packages.evidence_store.retention import live_holds, maybe_expire_llm
        from tests.helpers import fixture_with

        fixture = fixture_with(
            [
                {
                    "source": "data/legal_holds.csv",
                    "records": [{"hold_id": "LH-44", "scope": "NCB204-B24071", "status": "active"}],
                }
            ],
            scenario_id="HOLD-CACHE",
            workflow="privacy",
        )
        first = live_holds(fixture)
        second = live_holds(fixture)
        self.assertEqual(first[0]["hold_id"], "LH-44")
        self.assertEqual(second[0]["hold_id"], "LH-44")
        maybe_expire_llm(
            "REQ-HOLD-CACHE",
            recorded_at="2026-01-01T00:00:00+00:00",
            as_of="2026-08-01T08:00:00Z",
            record_type="llm",
            fixture=fixture,
        )
        rendered = json.dumps(CACHE.keys())
        self.assertNotIn("hold", rendered)
        self.assertEqual(CACHE.keys(), [])
