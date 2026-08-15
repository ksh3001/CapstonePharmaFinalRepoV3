from __future__ import annotations

import json
import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class DraftHasNoPowerTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_drafts_are_descriptions_with_no_side_effects(self) -> None:
        pack = advisory_pack(load_pub("PUB-13"))
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertTrue(pack["no_side_effects"])
        drafts = pack["human_review"]["preexisting_drafts"]
        self.assertEqual({item["draft_id"] for item in drafts}, {"DR-1", "DR-2"})
        for item in drafts:
            self.assertEqual(item["status"], "draft")
            self.assertTrue(item["no_side_effects"])
            rendered = json.dumps(item).casefold()
            self.assertNotIn("reservation that exists", rendered)
            self.assertNotIn("is reserved", rendered)
