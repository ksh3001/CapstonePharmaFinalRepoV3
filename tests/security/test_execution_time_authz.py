from __future__ import annotations

import copy
import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class ExecutionTimeAuthzTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_revoked_cached_contractor_is_denied_and_cites_both_sources(self) -> None:
        fixture = copy.deepcopy(load_pub("PUB-09"))
        fixture["authorized_context"]["user"] = "contractor_77"
        pack = advisory_pack(fixture)
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertEqual(pack["authorization"]["decision"], "deny")
        self.assertEqual(pack["authorization"]["reason"], "AUTHZ_DENIED")
        rendered = " ".join(pack["authorization"].get("reason", "").split())
        refs = " ".join(
            " ".join(item.get("evidence_refs") or []) + " " + item.get("statement", "")
            for item in pack["findings"]
        )
        self.assertIn("users_entitlements.csv", refs)
        self.assertIn("access_cache.csv", refs)
        self.assertEqual(rendered, "AUTHZ_DENIED")

    def test_removing_entitlement_cache_does_not_allow_contractor(self) -> None:
        fixture = copy.deepcopy(load_pub("PUB-09"))
        fixture["authorized_context"]["user"] = "contractor_77"
        fixture["evidence"] = [
            blob
            for blob in fixture["evidence"]
            if not str(blob.get("source") or "").replace("\\", "/").endswith("access_cache.csv")
        ]
        pack = advisory_pack(fixture)
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertEqual(pack["authorization"]["decision"], "deny")
        self.assertEqual(pack["authorization"]["reason"], "AUTHZ_DENIED")
