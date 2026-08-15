from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from services.api.handlers import handle, reset_api_state
from tests.security.test_sensitive_segments import _segment_fixture


class PayloadEntitlementTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()

    def test_unentitled_segment_is_absent_from_payload_body(self) -> None:
        response = handle("GET", "/api/workflows/pv/PV-1020", fixture=_segment_fixture("participant_test_user"))
        self.assertEqual(response["status"], 200)
        body = response["body"]
        self.assertNotIn("pregnancy", body.casefold())
        self.assertNotIn("pv_pregnancy", body.casefold())
