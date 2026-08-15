from __future__ import annotations

import copy
import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class RevocationLagTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_finding_names_revoked_at_and_cached_until_window(self) -> None:
        fixture = copy.deepcopy(load_pub("PUB-09"))
        fixture["authorized_context"]["user"] = "contractor_77"
        pack = advisory_pack(fixture)
        validate(pack, resolve_contract("advisory_nonexecuting"))
        statements = " ".join(item["statement"] for item in pack["findings"])
        self.assertIn("2026-08-01T05:00:00Z", statements)
        self.assertIn("2026-08-03T10:00:00Z", statements)
