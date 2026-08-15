from __future__ import annotations

import unittest

from services.api.console import render_pack_page


class DegradedStateTests(unittest.TestCase):
    def test_unavailable_api_names_runbook_and_hides_pack(self) -> None:
        html = render_pack_page(
            {
                "request_id": "REQ-x",
                "findings": [{"statement": "stale-finding"}],
                "gaps": [],
                "abstentions": [],
                "contradictions": [],
                "evidence": [],
                "human_review": {},
            },
            title="Batch",
            api_available=False,
            workflow="batch_review",
        )
        self.assertIn("docs/runbooks/batch_review.md", html)
        self.assertIn("no stale pack is current", html.casefold())
        self.assertNotIn("stale-finding", html)
