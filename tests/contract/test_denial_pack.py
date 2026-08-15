from __future__ import annotations

import copy
import json
import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class DenialPackTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_denied_request_is_schema_valid_and_empty_of_withheld_content(self) -> None:
        fixture = copy.deepcopy(load_pub("PUB-09"))
        fixture["authorized_context"]["user"] = "contractor_77"
        pack = advisory_pack(fixture)
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertEqual(pack["authorization"]["decision"], "deny")
        self.assertEqual(pack["execution_status"], "not_executed")
        self.assertTrue(pack["no_side_effects"])
        self.assertEqual(pack["evidence"], [])
        rendered = json.dumps(pack).casefold()
        self.assertNotIn("patient_id", rendered)
        self.assertNotIn("date_of_birth", rendered)
        self.assertNotIn("initials", rendered)
