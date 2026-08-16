from __future__ import annotations

import re
import unittest

from packages.kernel.checkpoint import reset_replay
from services.api.handlers import outstanding_critical, reset_api_state
from services.api.server import dispatch, reset_server_state


class ConsoleServerTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()
        reset_server_state()

    def test_user_guide_opens_from_header(self) -> None:
        home = dispatch("GET", "/")
        self.assertIn('id="guide-toggle"', home["body"])
        self.assertIn('id="user-guide"', home["body"])
        self.assertIn("User guide", home["body"])
        self.assertIn('for="guide-toggle"', home["body"])
        self.assertIn("Batch evidence", home["body"])
        self.assertIn("PV intake", home["body"])
        self.assertIn("Supply / cold-chain", home["body"])
        self.assertIn("Pack chat", home["body"])
        self.assertIn("guide-shot", home["body"])
        self.assertIn("/static/guide/home.jpg", home["body"])
        self.assertIn("/static/guide/workflows-batch.jpg", home["body"])
        self.assertIn("<img ", home["body"])
        start = home["body"].find('id="user-guide"')
        self.assertGreaterEqual(start, 0)
        self.assertNotIn("allocate", home["body"][start:].casefold())

    def test_home_and_batch_html(self) -> None:
        home = dispatch("GET", "/home")
        self.assertEqual(home["status"], 200)
        self.assertIn("text/html", home["headers"]["content-type"])
        self.assertIn("/workflows/batch", home["body"])
        self.assertIn("/health", home["body"])
        self.assertIn("Runtime health", home["body"])
        self.assertIn("health-strip", home["body"])
        self.assertIn("Open full telemetry", home["body"])
        page = dispatch("GET", "/workflows/batch")
        self.assertEqual(page["status"], 200)
        self.assertIn("NCB204-B24071", page["body"])
        self.assertIn("qp_eu_1", page["body"])
        self.assertIn("EU Qualified Person", page["body"])
        self.assertIn("remaining critical evidence", page["body"].casefold())
        self.assertIn("CMO audit commitment 2025-14", page["body"])
        self.assertIn("cmo_commitment_missing", page["body"])
        self.assertIn("missing_branch", page["body"])
        self.assertIn("mg/L", page["body"])
        self.assertIn("work-table", page["body"])
        self.assertIn("Knowledge graph · per-run projection", page["body"])
        self.assertIn("Not a system of record", page["body"])
        self.assertNotIn("Agent graph · declared steps", page["body"])
        self.assertNotIn("step-rail", page["body"])
        self.assertNotIn("Orchestrator steps", page["body"])

    def test_json_api_is_unchanged(self) -> None:
        response = dispatch("GET", "/api/workflows/batch/NCB204-B24071", user="preparer_1")
        self.assertEqual(response["status"], 200)
        pack = response["payload"]
        self.assertEqual(pack["batch_id"], "NCB204-B24071")
        self.assertEqual(pack["execution_status"], "not_executed")

    def test_opening_evidence_then_acknowledge(self) -> None:
        page = dispatch("GET", "/workflows/batch/NCB204-B24071")
        match = re.search(r"request_id=([^\"&]+)", page["body"])
        self.assertIsNotNone(match)
        request_id = match.group(1)
        self.assertIn("remaining critical evidence", page["body"].casefold())
        self.assertIn("Graphical view", page["body"])
        self.assertIn("pack-chart", page["body"])
        self.assertIn("Equal prominence", page["body"])
        self.assertIn("Critical evidence opened", page["body"])
        self.assertIn("bar-chart", page["body"])
        self.assertNotIn("Pack composition", page["body"])
        for record_id in outstanding_critical(request_id):
            opened = dispatch(
                "GET",
                f"/evidence/{record_id}",
                query={"request_id": [request_id]},
                user="reviewer_9",
            )
            self.assertEqual(opened["status"], 200)
        ready = dispatch("GET", "/workflows/batch/NCB204-B24071", query={"request_id": [request_id]})
        self.assertIn('class="ack"', ready["body"])
        result = dispatch("POST", f"/api/reviews/{request_id}/acknowledge", user="reviewer_9")
        self.assertEqual(result["status"], 200)
        self.assertTrue(result["payload"]["recorded"])

    def test_status_page_records_follow_up_as_evidence(self) -> None:
        dispatch("GET", "/workflows/batch/NCB204-B24071")
        status = dispatch("GET", "/status")
        self.assertEqual(status["status"], 200)
        self.assertIn("Workflow status", status["body"])
        self.assertIn("status-ring", status["body"])
        self.assertIn("hx-post=", status["body"])
        self.assertIn("follow-form", status["body"])
        self.assertIn("Store follow-up as evidence", status["body"])
        match = re.search(r"/api/reviews/(REQ-[^/]+)/contest", status["body"])
        self.assertIsNotNone(match)
        request_id = match.group(1)
        stored = dispatch(
            "POST",
            f"/api/reviews/{request_id}/contest",
            body={
                "reason": "missing commitment needs quality follow-up",
                "action_taken": "Asked quality for the CMO commitment packet",
            },
            user="reviewer_9",
        )
        self.assertEqual(stored["status"], 200)
        self.assertTrue(stored["payload"]["recorded"])
        again = dispatch("GET", "/status")
        self.assertIn("Asked quality for the CMO commitment packet", again["body"])
        self.assertIn("follow_up_recorded", again["body"])
        history = dispatch("GET", "/history")
        self.assertEqual(history["status"], 200)
        self.assertIn("Evidence history", history["body"])
        self.assertIn("Asked quality for the CMO commitment packet", history["body"])
        self.assertIn("not signatures", history["body"].casefold())
        self.assertIn("out/evidence/chains", history["body"])
        ledger = dispatch("GET", "/api/history")
        self.assertEqual(ledger["status"], 200)
        self.assertEqual(ledger["payload"]["store"], "evidence_chain")
        events = ledger["payload"]["events"]
        self.assertTrue(any(item.get("event") == "contest" and "CMO commitment" in str(item.get("action_taken") or "") for item in events))
        home = dispatch("GET", "/home")
        self.assertIn("/history", home["body"])

    def test_contradictions_board_records_per_item_follow_up(self) -> None:
        page = dispatch("GET", "/contradictions")
        self.assertEqual(page["status"], 200)
        self.assertIn("Consolidated contradictions", page["body"])
        self.assertIn("Position A", page["body"])
        self.assertIn("subject_id", page["body"])
        self.assertIn("hx-post=", page["body"])
        self.assertIn("follow-form", page["body"])
        self.assertIn("Store follow-up as evidence", page["body"])
        self.assertIn('id="aegis-toast"', page["body"])
        match = re.search(r'name="subject_id" value="([^"]+)"', page["body"])
        req = re.search(r"/api/reviews/(REQ-[^/]+)/contest", page["body"])
        self.assertIsNotNone(match)
        self.assertIsNotNone(req)
        stored = dispatch(
            "POST",
            f"/api/reviews/{req.group(1)}/contest",
            body={
                "subject_id": match.group(1),
                "reason": f"contradiction:{match.group(1)}",
                "action_taken": "Asked MES and warehouse to confirm SUA-88",
            },
            user="reviewer_9",
        )
        self.assertEqual(stored["status"], 200)
        again = dispatch("GET", "/contradictions")
        self.assertIn("Asked MES and warehouse to confirm SUA-88", again["body"])

    def test_gates_page_explains_controls(self) -> None:
        page = dispatch("GET", "/gates")
        self.assertIn("There is no switch here to turn a gate off", page["body"])
        self.assertIn("authz", page["body"])
        self.assertIn("Oversight", page["body"])
        self.assertIn("not a work queue", page["body"].casefold())
        css = dispatch("GET", "/static/aegis.css")
        sheet = css["body"].decode("utf-8") if isinstance(css["body"], bytes) else str(css["body"])
        self.assertIn("nav-toggle", sheet)
        self.assertIn("max-width: 640px", sheet)
        self.assertIn("minmax(min(100%", sheet)
        self.assertIn(".viewed-check:checked + .viewed-mark", sheet)
        self.assertIn('input:not([type="checkbox"])', sheet)
        self.assertIn(".follow-form", sheet)
        self.assertIn(".toast", sheet)
        self.assertIn("input.viewed-check[type=\"checkbox\"]", sheet)
        self.assertIn(".top-search input[type=\"search\"]", sheet)
        self.assertIn("flex: 1 1 auto", sheet)
        self.assertIn("minmax(22rem, 1fr)", sheet)
        self.assertIn("max-width: none", sheet)
        self.assertNotIn("max-width: min(520px, 100%)", sheet)
        self.assertNotIn(".top-search input { width: auto; }", sheet)

    def test_injects_page_shows_coverage(self) -> None:
        page = dispatch("GET", "/injects")
        self.assertEqual(page["status"], 200)
        self.assertIn("INJ-001", page["body"])
        self.assertIn("Covered · artefact", page["body"])
        self.assertIn("INJ-021", page["body"])
        self.assertIn("Covered", page["body"])
        self.assertIn("not covered", page["body"].casefold())
        css = dispatch("GET", "/static/aegis.css")
        sheet = css["body"].decode("utf-8") if isinstance(css["body"], bytes) else str(css["body"])
        self.assertIn(".chip.ok", sheet)
        self.assertIn(".inject-row", sheet)
        payload = dispatch("GET", "/api/injects/coverage")
        self.assertEqual(payload["status"], 200)
        rows = {item["id"]: item for item in payload["payload"]["injects"]}
        self.assertEqual(rows["INJ-001"]["coverage"], "artefact")
        self.assertTrue(rows["INJ-001"]["covered"])
        self.assertEqual(rows["INJ-021"]["coverage"], "covered")
        self.assertTrue(rows["INJ-021"]["covered"])
        self.assertIn("business_rules", rows["INJ-021"])
        self.assertTrue(rows["INJ-021"]["business_rules"] or rows["INJ-021"]["acceptance_criteria"])
        counts = payload["payload"]["counts"]
        self.assertEqual(counts["artefact"], 3)
        self.assertGreaterEqual(counts["covered"], 1)
        self.assertEqual(counts["uncovered"], 0)
        self.assertEqual(len(rows), 84)
        self.assertEqual(counts["covered"] + counts["artefact"] + counts["uncovered"], 84)
        self.assertEqual(rows["INJ-001"]["artefact_path"], "docs/product/business-case.md")
        self.assertIn("test_benefit_claims.py", rows["INJ-001"]["verifying_test"])
        self.assertIn("covers all 84", page["body"])
        self.assertIn("do not each carry all 84", page["body"])
        self.assertIn("Evidence ", page["body"])
        self.assertIn("material_genealogy.csv", page["body"])
        self.assertIn("test_batch_contradictions.py", page["body"])
        self.assertIn("test_benefit_claims.py", page["body"])
        self.assertEqual(rows["INJ-021"]["lane"], "Batch")
        self.assertIn("material_genealogy.csv", rows["INJ-021"]["evidence_sources"])
        self.assertTrue(rows["INJ-021"]["verifying_tests"])

    def test_agents_page_lists_six_roles(self) -> None:
        page = dispatch("GET", "/agents")
        self.assertEqual(page["status"], 200)
        self.assertIn("AG-1", page["body"])
        self.assertIn("Supervisor", page["body"])
        self.assertIn("AG-6", page["body"])
        self.assertIn("They do not decide", page["body"])
        home = dispatch("GET", "/home")
        self.assertIn("/agents", home["body"])

    def test_health_page_is_in_process_not_otel(self) -> None:
        page = dispatch("GET", "/health")
        self.assertEqual(page["status"], 200)
        self.assertIn("Runtime health", page["body"])
        self.assertIn("not opentelemetry", page["body"].casefold())
        self.assertIn("evidence chain", page["body"].casefold())
        self.assertIn("Token utilisation", page["body"])
        self.assertIn("LLM cost", page["body"])
        self.assertIn("partial", page["body"].casefold())
        self.assertIn("listed unit prices", page["body"].casefold())
        self.assertIn("Control plane", page["body"])
        self.assertIn("health-banner", page["body"])
        self.assertIn("health-stack", page["body"])
        self.assertNotIn("estimated cost", page["body"].casefold())
        self.assertNotIn("assumed cost", page["body"].casefold())
        self.assertIn("/api/health", page["body"])
        home = dispatch("GET", "/home")
        self.assertIn("/health", home["body"])
        self.assertIn("Runtime health", home["body"])
        payload = dispatch("GET", "/api/health")
        self.assertEqual(payload["status"], 200)
        snap = payload["payload"]
        self.assertEqual(snap["telemetry"], "evidence_chain")
        self.assertEqual(snap["store"], "in_process")
        self.assertTrue(snap["advisory"])
        self.assertIn("total_tokens", snap)
        self.assertIn("prompt_tokens", snap)
        self.assertIn("token_ceiling", snap)
        self.assertIn("cost", snap)
        self.assertFalse(snap["cost"]["estimated"])
        css = dispatch("GET", "/static/aegis.css")
        sheet = css["body"].decode("utf-8") if isinstance(css["body"], bytes) else str(css["body"])
        self.assertIn(".health-meter", sheet)
        self.assertIn(".health-fill", sheet)
        self.assertIn(".health-banner", sheet)
        self.assertIn(".health-stack", sheet)

    def test_home_and_modules_list_every_selectable_id(self) -> None:
        home = dispatch("GET", "/home")
        for entity_id in (
            "NCB204-B24071",
            "NCS310-S26033",
            "PV-1001",
            "PV-1009",
            "PV-1014",
            "SM-77",
            "SH-901",
            "SH-902",
            "NCB-204-shortage",
        ):
            self.assertIn(entity_id, home["body"])
        self.assertIn("Product NCB-204", home["body"])
        self.assertIn("Product NCS-310", home["body"])
        self.assertIn("product-heading", home["body"])
        self.assertIn("By product", home["body"])
        self.assertIn("By workflow", home["body"])
        self.assertIn("What reviewers must inspect", home["body"])
        self.assertIn("Equal prominence", home["body"])
        self.assertNotIn("Pack composition", home["body"])
        self.assertNotIn("Review load", home["body"])
        batch = dispatch("GET", "/workflows/batch")
        self.assertIn("entity-picker", batch["body"])
        self.assertIn("<select", batch["body"])
        self.assertIn("Batch id", batch["body"])
        self.assertIn('value="NCS310-S26033"', batch["body"])
        self.assertIn("Product NCB-204", batch["body"])
        self.assertIn("Product NCS-310", batch["body"])
        self.assertIn("<optgroup", batch["body"])
        self.assertNotIn("Store comment as evidence", batch["body"])
        self.assertNotIn("Comment or contest reason", batch["body"])
        second = dispatch("GET", "/workflows/batch/NCS310-S26033")
        self.assertEqual(second["status"], 200)
        self.assertIn("NCS310-S26033", second["body"])
        self.assertIn("selected", second["body"])
        via_query = dispatch("GET", "/workflows/batch", query={"entity": ["NCS310-S26033"]})
        self.assertEqual(via_query["status"], 200)
        self.assertIn("NCS310-S26033", via_query["body"])
        pv = dispatch("GET", "/workflows/pv")
        self.assertIn("Case or signal id", pv["body"])
        self.assertIn("<select", pv["body"])
        self.assertIn('value="PV-1014"', pv["body"])
        supply = dispatch("GET", "/workflows/supply")
        self.assertIn("Shipment or event id", supply["body"])
        self.assertIn('value="SH-902"', supply["body"])
        self.assertIn("Product NCS-310", supply["body"])
        second_supply = dispatch("GET", "/workflows/supply/SH-902")
        self.assertIn("Product NCS-310", second_supply["body"])
        status = dispatch("GET", "/status")
        self.assertIn("NCS310-S26033", status["body"])
        board = dispatch("GET", "/contradictions")
        self.assertIn("NCS310-S26033", board["body"])

    def test_second_batch_api_uses_pub_02(self) -> None:
        response = dispatch("GET", "/api/workflows/batch/NCS310-S26033", user="preparer_1")
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["payload"]["batch_id"], "NCS310-S26033")

    def test_search_routes_catalog_ids(self) -> None:
        page = dispatch("GET", "/search", query={"q": ["SM-77"]})
        self.assertEqual(page["status"], 200)
        self.assertIn("SM-77", page["body"])

    def test_each_id_stores_its_own_action_taken_comment(self) -> None:
        first = dispatch("GET", "/workflows/supply/SH-901")
        second = dispatch("GET", "/workflows/supply/SH-902")
        req_a = re.search(r"Request (REQ-[^<]+)", first["body"])
        req_b = re.search(r"Request (REQ-[^<]+)", second["body"])
        self.assertIsNotNone(req_a)
        self.assertIsNotNone(req_b)
        self.assertNotEqual(req_a.group(1), req_b.group(1))
        stored = dispatch(
            "POST",
            f"/api/reviews/{req_a.group(1)}/contest",
            body={
                "reason": "logger association needs follow-up",
                "action_taken": "Asked logistics to confirm LG-31 for SH-901",
                "subject_id": "SH-901",
            },
            user="reviewer_9",
        )
        self.assertEqual(stored["status"], 200)
        status = dispatch("GET", "/status")
        self.assertIn("Asked logistics to confirm LG-31 for SH-901", status["body"])
        other = dispatch("GET", "/workflows/supply/SH-902")
        self.assertNotIn("Asked logistics to confirm LG-31 for SH-901", other["body"])
        pack = dispatch("GET", "/workflows/supply/SH-901")
        self.assertNotIn("Store comment as evidence", pack["body"])

    def test_ask_box_returns_engine_status_for_batch_id(self) -> None:
        home = dispatch("GET", "/home")
        self.assertIn("Pack chat", home["body"])
        self.assertIn('hx-post="/api/ask"', home["body"])
        self.assertIn('hx-target="#engine-thread"', home["body"])
        self.assertIn("chat-fab", home["body"])
        self.assertIn("Advisory chatbot", home["body"])
        self.assertIn("Not a disposition", home["body"])
        json_ask = dispatch(
            "POST",
            "/api/ask",
            body={"q": "What is the status of NCB204-B24071?"},
            user="qp_eu_1",
        )
        self.assertEqual(json_ask["status"], 200)
        payload = json_ask["payload"]
        self.assertTrue(payload["ok"])
        self.assertIn("NCB204-B24071", payload["answer"])
        self.assertIn("Readiness", payload["answer"])
        self.assertIn("Advisory only", payload["answer"])
        self.assertFalse(payload.get("disposition"))
        html_ask = dispatch(
            "POST",
            "/api/ask",
            body={"q": "status of NCB204-B24071"},
            user="qp_eu_1",
            hx=True,
        )
        self.assertEqual(html_ask["status"], 200)
        self.assertIn("ask-answer", html_ask["body"])
        self.assertIn("chat-card", html_ask["body"])
        self.assertIn("chat-bubble", html_ask["body"])
        self.assertIn("MCP · get_evidence_pack", html_ask["body"])
        self.assertIn("Remaining critical", html_ask["body"])
        self.assertTrue(
            "Do next" in html_ask["body"]
            or "Why" in html_ask["body"]
            or "No model summary" in html_ask["body"]
        )
        self.assertIn("NCB204-B24071", html_ask["body"])
        graph_ask = dispatch(
            "POST",
            "/api/ask",
            body={"q": "What is linked to NCB204-B24071?"},
            user="qp_eu_1",
            hx=True,
        )
        self.assertEqual(graph_ask["status"], 200)
        self.assertIn("get_graph_neighbourhood", graph_ask["body"])
        self.assertIn("Related nodes", graph_ask["body"])
        self.assertIn("LR-88", graph_ask["body"])
        refused = dispatch(
            "POST",
            "/api/ask",
            body={"q": "release the batch NCB204-B24071"},
            user="qp_eu_1",
        )
        self.assertFalse(refused["payload"]["ok"])
        self.assertIn("does not decide", refused["payload"]["answer"])
