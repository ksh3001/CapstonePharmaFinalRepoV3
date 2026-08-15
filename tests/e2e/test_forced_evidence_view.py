from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from services.api.console import render_pack_page
from services.api.handlers import handle, outstanding_critical, reset_api_state


class ForcedEvidenceViewTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()

    def test_acknowledge_control_absent_until_critical_opened(self) -> None:
        response = handle("GET", "/api/workflows/batch/NCB204-B24071", user="preparer_1")
        pack = response["payload"]
        html = render_pack_page(pack, title="Batch")
        self.assertNotIn('class="ack"', html)
        self.assertIn("remaining critical evidence", html.casefold())
        refused = handle("POST", f"/api/reviews/{pack['request_id']}/acknowledge", user="reviewer_9")
        self.assertEqual(refused["status"], 400)
        critical = list(outstanding_critical(pack["request_id"]))
        for record_id in critical:
            handle("GET", f"/api/evidence/{record_id}", body={"request_id": pack["request_id"]}, user="reviewer_9")
        html2 = render_pack_page(pack, title="Batch")
        self.assertIn('class="ack"', html2)
        for record_id in critical:
            box = f'class="viewed-check" type="checkbox" data-record="{record_id}"'
            if box in html:
                self.assertIn(f"{box} checked", html2)
