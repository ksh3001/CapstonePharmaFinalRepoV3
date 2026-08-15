from __future__ import annotations

import unittest

from packages.kernel.audit import audit_events, reset_audit
from packages.kernel.checkpoint import reset_replay
from services.api.console import render_pack_page
from services.api.handlers import handle, outstanding_critical, reset_api_state


class AcknowledgementTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()
        reset_audit()

    def test_acknowledgement_is_audited_and_not_a_signature(self) -> None:
        response = handle("GET", "/api/workflows/batch/NCB204-B24071", user="preparer_1")
        pack = response["payload"]
        for record_id in outstanding_critical(pack["request_id"]):
            handle("GET", f"/api/evidence/{record_id}", body={"request_id": pack["request_id"]}, user="reviewer_9")
        result = handle("POST", f"/api/reviews/{pack['request_id']}/acknowledge", user="reviewer_9")
        self.assertEqual(result["status"], 200)
        self.assertFalse(result["payload"]["signature"])
        self.assertIn("not an electronic signature", result["payload"]["label"].casefold())
        html = render_pack_page(pack, title="Batch")
        self.assertIn("not a signature", html.casefold())
        self.assertTrue(any(item.get("event") == "acknowledge" and item.get("signature") is False for item in audit_events()))
        self.assertTrue(any(item.get("pack_hash") for item in audit_events() if item.get("event") == "acknowledge"))
        from packages.evidence_store.chain import load_chain

        review = [row for row in load_chain(pack["request_id"]) if row.get("type") == "review"]
        self.assertTrue(any(row["payload"].get("event") == "acknowledge" for row in review))
        self.assertTrue(all(row["payload"].get("signature") is False for row in review))
