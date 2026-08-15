from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from services.api.handlers import reset_api_state
from services.api.server import dispatch, reset_server_state


class SessionIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()
        reset_server_state()

    def test_header_shows_fixture_identity(self) -> None:
        page = dispatch("GET", "/")
        self.assertIn("qp_eu_1", page["body"])
        self.assertIn("EU Qualified Person", page["body"])
        self.assertIn('class="identity-picker"', page["body"])
        self.assertIn("contractor_77", page["body"])
        self.assertIn("not assumable", page["body"])
        self.assertNotIn(">Reviewer<", page["body"])

    def test_session_post_sets_cookie_for_assumable_user(self) -> None:
        result = dispatch("POST", "/session", body={"user": "qp_eu_1", "next": "/status"})
        self.assertEqual(result["status"], 303)
        self.assertEqual(result["headers"]["location"], "/status")
        self.assertIn("aegis_user=qp_eu_1", result["headers"]["set-cookie"])
        self.assertIn("HttpOnly", result["headers"]["set-cookie"])

    def test_revoked_identity_cannot_be_assumed(self) -> None:
        result = dispatch("POST", "/session", body={"user": "contractor_77", "next": "/"})
        self.assertEqual(result["status"], 400)
        self.assertIn("not assumable", result["body"].casefold())

    def test_unknown_identity_cannot_be_assumed(self) -> None:
        result = dispatch("POST", "/session", body={"user": "reviewer_9"})
        self.assertEqual(result["status"], 400)
