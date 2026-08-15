from __future__ import annotations

import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class AccountAttributionTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_shared_account_is_unattributable_and_two_device_login_does_not_deny(self) -> None:
        pack = advisory_pack(load_pub("PUB-09"))
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertEqual(pack["authorization"]["decision"], "allow")
        statements = " ".join(item["statement"] for item in pack["findings"]).casefold()
        self.assertIn("lab_shared_night", statements)
        self.assertIn("unattributable", statements)
        self.assertIn("cannot support a regulated decision", statements)
        self.assertIn("site_coordinator_14", statements)
        self.assertIn("login_from_two_devices", statements)
        self.assertIn("does not by itself deny", statements)
