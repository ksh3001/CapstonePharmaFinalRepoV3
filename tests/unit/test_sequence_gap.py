from __future__ import annotations

import unittest

from packages.kernel.packs import advisory_pack
from tests.unit.test_identity_conflict import regulatory_fixture


class SequenceGapTests(unittest.TestCase):
    def test_missing_sequence_is_named(self) -> None:
        pack = advisory_pack(regulatory_fixture())
        gaps = [item for item in pack["gaps"] if item.get("gap_type") == "sequence_gap"]
        self.assertTrue(gaps)
        self.assertIn("EU-0042", str(gaps[0].get("subject_id") or gaps[0].get("missing") or gaps[0]))
        self.assertNotIn("renumbered", str(pack).casefold())
