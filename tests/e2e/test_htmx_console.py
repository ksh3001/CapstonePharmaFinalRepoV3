from __future__ import annotations

import re
import unittest

from packages.kernel.checkpoint import reset_replay
from services.api.handlers import reset_api_state
from services.api.server import dispatch, reset_server_state


class HtmxConsoleTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()
        reset_server_state()

    def test_pages_load_htmx_and_use_partials(self) -> None:
        home = dispatch("GET", "/home")
        self.assertIn("/static/htmx.min.js", home["body"])
        self.assertIn('hx-post="/api/ask"', home["body"])
        page = dispatch("GET", "/workflows/batch")
        self.assertIn("hx-get=", page["body"])
        self.assertIn('hx-target="#evidence-drawer"', page["body"])
        self.assertIn('id="evidence-drawer"', page["body"])
        self.assertIn("/static/htmx.min.js", page["body"])

    def test_static_htmx_is_served(self) -> None:
        response = dispatch("GET", "/static/htmx.min.js")
        self.assertEqual(response["status"], 200)
        body = response["body"]
        text = body.decode("utf-8") if isinstance(body, bytes) else str(body)
        self.assertIn("hx-get", text)
        self.assertIn("el.checked = true", text)
        self.assertIn("hx-swap-oob", text)
        self.assertIn("chat-spinner", text)
        self.assertIn("is-waiting", text)
        css = dispatch("GET", "/static/aegis.css")
        self.assertEqual(css["status"], 200)

    def test_hx_request_returns_evidence_fragment(self) -> None:
        page = dispatch("GET", "/workflows/batch")
        self.assertEqual(page["status"], 200)
        pack = dispatch("GET", "/api/workflows/batch/NCB204-B24071", user="preparer_1")
        request_id = pack["payload"]["request_id"]
        record_id = pack["payload"]["evidence"][0]["record_id"]
        fragment = dispatch(
            "GET",
            f"/evidence/{record_id}",
            query={"request_id": [request_id]},
            user="reviewer_9",
            hx=True,
        )
        self.assertEqual(fragment["status"], 200)
        self.assertIn("data-region=\"evidence-detail\"", fragment["body"])
        self.assertNotIn("<nav", fragment["body"])

    def test_follow_up_stays_on_page_and_returns_saved_toast(self) -> None:
        page = dispatch("GET", "/contradictions")
        self.assertIn('hx-post=', page["body"])
        self.assertIn("Store follow-up as evidence", page["body"])
        match = re.search(r'name="subject_id" value="([^"]+)"', page["body"])
        req = re.search(r"/api/reviews/(REQ-[^/]+)/contest", page["body"])
        self.assertIsNotNone(match)
        self.assertIsNotNone(req)
        saved = dispatch(
            "POST",
            f"/api/reviews/{req.group(1)}/contest",
            body={
                "next": "/contradictions",
                "panel": "contradiction",
                "subject_id": match.group(1),
                "reason": f"contradiction:{match.group(1)}",
                "action_taken": "Asked MES and warehouse to confirm SUA-88",
            },
            user="reviewer_9",
            hx=True,
        )
        self.assertEqual(saved["status"], 200)
        self.assertIn("Data saved", saved["body"])
        self.assertIn("Asked MES and warehouse to confirm SUA-88", saved["body"])
        self.assertIn("follow-panel", saved["body"])
        self.assertIn("hx-swap-oob", saved["body"])
        self.assertNotIn("<!DOCTYPE html>", saved["body"])
        self.assertNotIn("<nav", saved["body"])
