from __future__ import annotations

import unittest

from packages.kernel.packs import advisory_pack
from tests.unit.test_identity_conflict import regulatory_fixture


class CommitmentDeadlineTests(unittest.TestCase):
    def test_all_candidate_deadlines_are_retained(self) -> None:
        pack = advisory_pack(regulatory_fixture())
        candidates = pack["human_review"]["regulatory"]["deadline_candidates"]
        bases = {item.get("basis") for item in candidates}
        self.assertIn("tracker", bases)
        self.assertIn("authority_letter", bases)
        self.assertIn("relative_to_receipt", bases)
        deadlines = {item.get("deadline") for item in candidates}
        self.assertIn("2026-10-15", deadlines)
        self.assertIn("2026-09-30", deadlines)
        self.assertIn("within 60 calendar days of receipt", deadlines)
        self.assertFalse(any(item.get("operative_date") for item in candidates))
        self.assertNotIn("operative_date", str(pack))
