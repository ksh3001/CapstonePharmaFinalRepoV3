from __future__ import annotations

import json
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub


class ModelSubstitutionTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_fallback_small_is_not_substituted_without_validation(self) -> None:
        pack = advisory_pack(load_pub("PUB-10"))
        continuity = pack["human_review"]["continuity"]
        self.assertFalse(continuity["fallback_substituted"])
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "missing_equivalent_validation"]
        self.assertTrue(gaps)
        statement = gaps[0]["statement"].casefold()
        self.assertIn("fallback_small", statement)
        self.assertIn("missing", statement)
        rendered = json.dumps(pack).casefold()
        self.assertIn("equivalent validation", rendered)
        self.assertFalse(continuity["fallback_substituted"])
