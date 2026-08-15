from __future__ import annotations

import unittest

from services.api.console import FOCUS_CSS, render_pack_page


class KeyboardTests(unittest.TestCase):
    def test_interactive_elements_are_native_and_focusable(self) -> None:
        html = render_pack_page(
            {"request_id": "REQ-x", "findings": [], "gaps": [], "abstentions": [], "contradictions": [], "evidence": [{"record_id": "E-1", "source": "s", "authority": "a", "effective_at": None, "retrieved_at": "t", "integrity": {"sha256": "b" * 64}}], "human_review": {}},
            title="Batch",
        )
        self.assertIn("<a ", html)
        self.assertIn("<button", html)
        self.assertIn("outline:3px solid", FOCUS_CSS)
        self.assertNotIn("onclick=", html)
        self.assertNotIn("tabindex=\"-1\"", html)
