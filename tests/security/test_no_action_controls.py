from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from services.api.console import CORE_ROUTES, render_pack_page
from services.api.handlers import handle, inventory, reset_api_state


class NoActionControlsTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()

    def test_mutation_inventory_is_exactly_acknowledge_and_contest(self) -> None:
        listed = inventory()["mutations"]
        self.assertEqual(len(listed), 2)
        self.assertTrue(all("acknowledge" in item or "contest" in item for item in listed))
        html = render_pack_page({"evidence": [], "findings": [], "gaps": [], "abstentions": [], "contradictions": [], "human_review": {}, "request_id": "REQ-x"}, title="Batch")
        lowered = html.casefold()
        for token in ("allocate", "reserve", "ship the", "initiate recall", "approved for release"):
            self.assertNotIn(token, lowered)
        self.assertEqual(len(CORE_ROUTES), 4)
