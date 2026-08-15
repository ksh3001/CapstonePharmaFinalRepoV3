from __future__ import annotations

import unittest

from packages.kernel.audit import audit_events, reset_audit
from packages.kernel.checkpoint import reset_replay
from services.api.handlers import handle, outstanding_critical, reset_api_state


class SegregationOfDutiesTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()
        reset_audit()

    def test_preparer_cannot_acknowledge(self) -> None:
        first = handle("GET", "/api/workflows/batch/NCB204-B24071", user="preparer_1")
        self.assertEqual(first["status"], 200)
        request_id = first["payload"]["request_id"]
        for record_id in outstanding_critical(request_id):
            handle("GET", f"/api/evidence/{record_id}", body={"request_id": request_id}, user="reviewer_9")
        refused = handle("POST", f"/api/reviews/{request_id}/acknowledge", user="preparer_1")
        self.assertEqual(refused["status"], 400)
        self.assertIn("preparer", refused["payload"]["error"]["message"].casefold())
        self.assertTrue(any(item.get("reason") == "segregation_of_duties" for item in audit_events()))
        allowed = handle("POST", f"/api/reviews/{request_id}/acknowledge", user="reviewer_9")
        self.assertEqual(allowed["status"], 200)
        self.assertFalse(allowed["payload"]["signature"])
