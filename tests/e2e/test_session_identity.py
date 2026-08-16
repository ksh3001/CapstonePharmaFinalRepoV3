from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from services.api.handlers import reset_api_state
from services.api.server import dispatch, reset_server_state

_DEMO = {"user": "qp_eu_1", "password": "aegis-demo"}


class SessionIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()
        reset_server_state()

    def test_header_shows_fixture_identity(self) -> None:
        page = dispatch("GET", "/home")
        self.assertIn("qp_eu_1", page["body"])
        self.assertIn("EU Qualified Person", page["body"])
        self.assertIn('href="/"', page["body"])
        self.assertNotIn(">Reviewer<", page["body"])

    def test_landing_is_demo_login(self) -> None:
        for path in ("/", "/login"):
            page = dispatch("GET", path)
            self.assertEqual(page["status"], 200, path)
            body = page["body"]
            self.assertIn("Sign in", body)
            self.assertIn('name="user"', body)
            self.assertIn('name="password"', body)
            self.assertIn('type="password"', body)
            self.assertIn('value="qp_eu_1"', body)
            self.assertIn(">Log in<", body)
            self.assertIn('action="/session"', body)
            self.assertIn('name="next" value="/home"', body)
            self.assertIn("login-panel", body)
            self.assertIn("<style>", body)
            self.assertNotIn("Entitlement roster", body)
            self.assertNotIn("Demo credentials", body)

    def test_session_post_sets_cookie_for_assumable_user(self) -> None:
        result = dispatch("POST", "/session", body={**_DEMO, "next": "/status"})
        self.assertEqual(result["status"], 303)
        self.assertEqual(result["headers"]["location"], "/status")
        self.assertIn("aegis_user=qp_eu_1", result["headers"]["set-cookie"])
        self.assertIn("HttpOnly", result["headers"]["set-cookie"])

    def test_session_post_maps_root_next_to_home(self) -> None:
        result = dispatch("POST", "/session", body={**_DEMO, "next": "/"})
        self.assertEqual(result["status"], 303)
        self.assertEqual(result["headers"]["location"], "/home")

    def test_wrong_password_is_rejected(self) -> None:
        result = dispatch(
            "POST",
            "/session",
            body={"user": "qp_eu_1", "password": "wrong", "next": "/home"},
        )
        self.assertEqual(result["status"], 401)
        self.assertIn("incorrect", result["body"].casefold())

    def test_revoked_identity_cannot_be_assumed(self) -> None:
        result = dispatch(
            "POST",
            "/session",
            body={"user": "contractor_77", "password": "aegis-demo", "next": "/home"},
        )
        self.assertEqual(result["status"], 400)
        self.assertIn("not assumable", result["body"].casefold())
        self.assertIn("Sign in", result["body"])

    def test_unknown_identity_cannot_be_assumed(self) -> None:
        result = dispatch(
            "POST",
            "/session",
            body={"user": "reviewer_9", "password": "aegis-demo"},
        )
        self.assertEqual(result["status"], 400)
