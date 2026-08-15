from __future__ import annotations

import unittest

from services.api.console import render_pack_page


class ContradictionRenderTests(unittest.TestCase):
    def test_both_positions_shown_without_resolve_control(self) -> None:
        html = render_pack_page(
            {
                "request_id": "REQ-x",
                "findings": [],
                "gaps": [],
                "abstentions": [],
                "contradictions": [
                    {"statement": "MES says issued", "source": "data/mes.csv", "record_id": "G-1", "topic": "genealogy"}
                ],
                "evidence": [],
                "human_review": {},
            },
            title="Batch",
        )
        self.assertIn("MES says issued", html)
        self.assertIn("data/mes.csv", html)
        self.assertIn("class=\"positions\"", html)
        self.assertNotIn("resolve", html.casefold())
        self.assertNotIn("accept left", html.casefold())
