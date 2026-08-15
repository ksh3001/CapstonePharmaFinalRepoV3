from __future__ import annotations

import unittest

from packages.kernel.checkpoint import reset_replay
from services.api.handlers import reset_api_state
from services.integration.mcp.ask import answer_question
from services.integration.mcp.tools import call_tool


class McpAskTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_api_state()

    def test_status_of_batch_id_uses_engine_pack(self) -> None:
        result = answer_question("What is the status of NCB204-B24071?", user="qp_eu_1")
        self.assertTrue(result["ok"])
        self.assertEqual(result["entity_id"], "NCB204-B24071")
        self.assertIn("NCB204-B24071", result["answer"])
        self.assertIn("Readiness", result["answer"])
        self.assertIn("NCB-204", result["answer"])
        self.assertIn("Advisory only", result["answer"])
        self.assertFalse(result["disposition"])
        self.assertIn("narrative", result)
        summary = result["summary"]
        self.assertTrue(summary["advisory"])
        self.assertFalse(summary["disposition"])
        self.assertIn(
            summary["readiness_state"],
            {"ready_for_authorized_review", "insufficient_evidence", "conflicted_evidence"},
        )

    def test_inject_question_returns_coverage_counts(self) -> None:
        result = answer_question("How many injects are covered?", user="qp_eu_1")
        self.assertTrue(result["ok"])
        self.assertIn("Inject coverage", result["answer"])
        self.assertIn("artefact", result["answer"])

    def test_decide_language_is_refused(self) -> None:
        result = answer_question("Please release the batch NCB204-B24071", user="qp_eu_1")
        self.assertFalse(result["ok"])
        self.assertIn("does not decide", result["answer"])

    def test_linked_to_batch_id_uses_relation_graph(self) -> None:
        result = answer_question("What is linked to NCB204-B24071?", user="qp_eu_1")
        self.assertTrue(result["ok"])
        self.assertEqual(result["tool"], "get_graph_neighbourhood")
        self.assertEqual(result["entity_id"], "NCB204-B24071")
        self.assertIn("relation graph", result["answer"])
        self.assertIn("batches.csv:NCB204-B24071", result["answer"])
        self.assertIn("LR-88", result["answer"])
        self.assertNotIn("Readiness", result["answer"])
        summary = result["summary"]
        self.assertEqual(summary["seed"], "batches.csv:NCB204-B24071")
        self.assertIn("lab_results.csv:LR-88", summary["visited"])
        self.assertTrue(summary["advisory"])

    def test_random_question_is_refused(self) -> None:
        result = answer_question("What is the weather in London?", user="qp_eu_1")
        self.assertFalse(result["ok"])
        self.assertIn("does not answer general questions", result["answer"])
        self.assertIn("NCB204-B24071", result["answer"])

    def test_graph_question_without_id_asks_for_catalog_id(self) -> None:
        result = answer_question("Show me the relation graph", user="qp_eu_1")
        self.assertFalse(result["ok"])
        self.assertIn("catalog id for the relation graph", result["answer"])

    def test_get_graph_neighbourhood_tool_returns_seed(self) -> None:
        result = call_tool("get_graph_neighbourhood", {"entity_id": "NCB204-B24071"}, user="qp_eu_1")
        self.assertTrue(result["ok"])
        self.assertEqual(result["summary"]["seed"], "batches.csv:NCB204-B24071")
        self.assertGreater(result["summary"]["visited_count"], 0)

    def test_get_evidence_pack_tool_summarises_catalog_id(self) -> None:
        result = call_tool("get_evidence_pack", {"entity_id": "NCB204-B24071"}, user="qp_eu_1")
        self.assertTrue(result["ok"])
        self.assertEqual(result["summary"]["entity"], "NCB204-B24071")
        self.assertEqual(result["summary"]["product"], "NCB-204")
        self.assertTrue(result["summary"]["advisory"])
