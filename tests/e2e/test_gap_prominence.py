from __future__ import annotations

import unittest

from services.api.console import render_pack_page


class GapProminenceTests(unittest.TestCase):
    def test_regions_are_siblings_and_not_collapsed(self) -> None:
        html = render_pack_page(
            {
                "request_id": "REQ-x",
                "findings": [{"statement": "finding-one"}],
                "gaps": [{"statement": "gap-one", "gap_type": "missing"}],
                "abstentions": [{"statement": "abstain-one", "reason_code": "x"}],
                "contradictions": [{"statement": "left", "source": "a", "record_id": "r1", "topic": "t"}],
                "evidence": [],
                "human_review": {},
            },
            title="Batch",
        )
        self.assertIn("data-region=\"findings\"", html)
        self.assertIn("data-region=\"gaps\"", html)
        self.assertIn("data-region=\"abstentions\"", html)
        self.assertIn("data-region=\"contradictions\"", html)
        self.assertNotIn("collapsed", html.casefold())
        self.assertNotIn("<details", html)
        pos_f = html.find("data-region=\"findings\"")
        pos_g = html.find("data-region=\"gaps\"")
        pos_a = html.find("data-region=\"abstentions\"")
        self.assertLess(pos_f, pos_g)
        self.assertLess(pos_g, pos_a)
