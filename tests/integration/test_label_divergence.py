from __future__ import annotations

import unittest

from packages.contracts.deny import assert_clean
from packages.kernel.packs import advisory_pack
from tests.unit.test_identity_conflict import regulatory_fixture


class LabelDivergenceTests(unittest.TestCase):
    def test_markets_are_retained_without_merged_text(self) -> None:
        pack = advisory_pack(regulatory_fixture())
        labels = pack["human_review"]["regulatory"]["labels"]
        markets = {item.get("market") for item in labels}
        self.assertEqual(markets, {"EU", "US"})
        texts = {item.get("risk_text") for item in labels}
        self.assertIn("severe infusion reactions including anaphylaxis", texts)
        self.assertIn("serious infusion reactions", texts)
        self.assertFalse(any("merged" in str(item).casefold() for item in labels))
        rendered = str(pack)
        self.assertNotIn("merged_label", rendered)
        assert_clean(pack)
