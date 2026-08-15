from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from services.api.handlers import reset_api_state
from services.api.server import reset_server_state

try:
    from fastapi.testclient import TestClient

    from services.api.fastapi_app import create_app
except ImportError:  # pragma: no cover - assessment has no FastAPI
    TestClient = None  # type: ignore[misc, assignment]
    create_app = None  # type: ignore[misc, assignment]


@unittest.skipUnless(TestClient is not None, "FastAPI is optional (requirements-ui.txt)")
class FastAPIConsoleTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()
        reset_server_state()
        self.client = TestClient(create_app())

    def test_home_and_batch_are_html(self) -> None:
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn("text/html", home.headers["content-type"])
        self.assertIn("/workflows/batch", home.text)
        self.assertIn("/health", home.text)
        self.assertIn("Runtime health", home.text)
        self.assertIn("health-strip", home.text)
        self.assertIn("Open full telemetry", home.text)
        page = self.client.get("/workflows/batch/NCB204-B24071")
        self.assertEqual(page.status_code, 200)
        lowered = page.text.casefold()
        self.assertIn("ncb204-b24071", lowered)
        self.assertIn("hx-get=", page.text)
        self.assertIn("not_executed", lowered)
        self.assertTrue(
            "remaining critical evidence" in lowered or 'class="ack"' in page.text,
            "batch pack must show the acknowledge gate or the acknowledge control",
        )

    def test_json_api_still_returns_pack(self) -> None:
        response = self.client.get("/api/workflows/batch/NCB204-B24071", headers={"X-Aegis-User": "preparer_1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["batch_id"], "NCB204-B24071")
        self.assertEqual(response.json()["execution_status"], "not_executed")

    def test_session_cookie_is_set_for_fixture_user(self) -> None:
        response = self.client.post("/session", data={"user": "qp_eu_1", "next": "/"}, follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertIn("aegis_user=qp_eu_1", response.headers.get("set-cookie", ""))
        home = self.client.get("/")
        self.assertIn("qp_eu_1", home.text)
        self.assertIn("EU Qualified Person", home.text)

    def test_health_page_is_html(self) -> None:
        page = self.client.get("/health")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Runtime health", page.text)
        self.assertIn("not opentelemetry", page.text.casefold())
        snap = self.client.get("/api/health")
        self.assertEqual(snap.status_code, 200)
        self.assertEqual(snap.json()["telemetry"], "evidence_chain")
