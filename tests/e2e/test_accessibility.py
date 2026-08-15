from __future__ import annotations

import unittest

from services.api.console import FOCUS_CSS, render_pack_page


class AccessibilityTests(unittest.TestCase):
    def test_core_screen_has_lang_headings_and_no_unlabelled_controls(self) -> None:
        html = render_pack_page(
            {"request_id": "REQ-x", "findings": [], "gaps": [], "abstentions": [], "contradictions": [], "evidence": [], "human_review": {}},
            title="Batch review",
        )
        self.assertIn('lang="en"', html)
        self.assertIn("<h1>", html)
        self.assertIn("<h2>", html)
        self.assertIn("outline:3px solid", FOCUS_CSS)
        self.assertNotIn("aria-hidden=\"true\"", html)
