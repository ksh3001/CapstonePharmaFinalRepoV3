from __future__ import annotations

import unittest

from services.api.console import render_pack_page

PACK = {
    "request_id": "REQ-x",
    "findings": [{"statement": "same-finding"}],
    "gaps": [],
    "abstentions": [],
    "contradictions": [],
    "evidence": [],
    "human_review": {},
}


class RtlAndScriptsTests(unittest.TestCase):
    def test_arabic_is_rtl_and_values_match_latin(self) -> None:
        en = render_pack_page(PACK, title="Review", locale="en")
        ar = render_pack_page(PACK, title="Review", locale="ar")
        hi = render_pack_page(PACK, title="Review", locale="hi")
        self.assertIn('dir="rtl"', ar)
        self.assertIn('dir="ltr"', en)
        self.assertIn("same-finding", en)
        self.assertIn("same-finding", ar)
        self.assertIn("same-finding", hi)
        self.assertIn("समीक्षा", hi)
