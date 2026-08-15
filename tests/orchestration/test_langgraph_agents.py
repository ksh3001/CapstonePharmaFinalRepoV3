from __future__ import annotations

import os
import unittest

from packages.config.agents import AGENT_IDS, load_agents, tool_allowed
from packages.kernel.audit import audit_events, reset_audit
from packages.kernel.checkpoint import reset_replay
from packages.orchestrator.deterministic import StdlibOrchestrator
from packages.orchestrator.graph import DECLARED_STEPS, role_for_step
from packages.orchestrator.resolve import resolve_orchestrator
from services.integration.langgraph.adapter import LangGraphOrchestrator
from services.integration.langgraph.resolve import resolve_runtime_orchestrator
from tests.helpers import load_pub


def _langgraph_present() -> bool:
    try:
        from langgraph.graph import StateGraph  # noqa: F401

        return True
    except ImportError:
        return False


class AgentConfigTests(unittest.TestCase):
    def test_six_runtime_roles_are_declared(self) -> None:
        agents = load_agents()
        self.assertEqual(tuple(agents), AGENT_IDS)
        self.assertFalse(agents["AG-1"]["inference"])
        self.assertFalse(agents["AG-6"]["inference"])
        self.assertTrue(agents["AG-3"]["inference"])
        self.assertIn("approve", agents["AG-1"]["interrupts"])
        self.assertFalse(tool_allowed("AG-1", "write_stock"))

    def test_step_roles_are_fixed(self) -> None:
        self.assertEqual(role_for_step("plan"), "AG-1")
        self.assertEqual(role_for_step("project_graph"), "AG-2")
        self.assertEqual(role_for_step("reconcile", "batch"), "AG-3")
        self.assertEqual(role_for_step("reconcile", "pv"), "AG-4")
        self.assertEqual(role_for_step("reconcile", "supply"), "AG-5")
        self.assertEqual(role_for_step("package"), "AG-6")
        self.assertEqual(role_for_step("validate_emit"), "kernel")


class LangGraphAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_audit()

    def test_assessment_resolver_stays_stdlib(self) -> None:
        self.assertIsInstance(resolve_orchestrator(), StdlibOrchestrator)

    def test_advisory_resolver_is_langgraph(self) -> None:
        old = os.environ.get("AEGIS_RUNTIME_MODE")
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "advisory"
            self.assertIsInstance(resolve_runtime_orchestrator(), LangGraphOrchestrator)
            os.environ["AEGIS_RUNTIME_MODE"] = "assessment"
            self.assertIsInstance(resolve_runtime_orchestrator(), StdlibOrchestrator)
        finally:
            if old is None:
                os.environ.pop("AEGIS_RUNTIME_MODE", None)
            else:
                os.environ["AEGIS_RUNTIME_MODE"] = old

    def test_langgraph_run_records_declared_roles(self) -> None:
        pack = LangGraphOrchestrator().run(
            {"fixture": load_pub("PUB-01"), "workflow": "batch", "entity_id": "NCB204-B24071"}
        )
        orch = pack["human_review"]["orchestration"]
        self.assertEqual(orch["steps_completed"], list(DECLARED_STEPS))
        self.assertEqual(orch["step_roles"][0], "kernel")
        self.assertEqual(orch["step_roles"][3], "AG-2")
        self.assertEqual(orch["step_roles"][4], "AG-3")
        self.assertEqual(orch["step_roles"][7], "AG-6")
        if _langgraph_present():
            self.assertEqual(orch["runner"], "langgraph")

    def test_undeclared_tool_is_refused(self) -> None:
        StdlibOrchestrator().run(
            {
                "fixture": load_pub("PUB-13"),
                "proposed_tools": ["write_stock"],
            }
        )
        self.assertTrue(any(item.get("event") == "excessive_agency" for item in audit_events()))

    @unittest.skipUnless(_langgraph_present(), "langgraph is optional")
    def test_approve_interrupt_resumes_to_a_finished_pack(self) -> None:
        runner = LangGraphOrchestrator()
        paused = runner.run({"fixture": load_pub("PUB-13"), "interrupt_on_approve": True})
        self.assertEqual(paused.get("gate_outcome"), "awaiting_human")
        self.assertEqual((paused.get("human_review") or {}).get("interrupt", {}).get("step"), "approve")
        self.assertEqual((paused.get("human_review") or {}).get("interrupt", {}).get("agent"), "AG-1")
        finished = runner.resume({"reviewer": "reviewer_9", "acknowledged": []})
        self.assertEqual(finished["human_review"]["orchestration"]["steps_completed"], list(DECLARED_STEPS))
        self.assertEqual(finished["execution_status"], "not_executed")
        self.assertNotEqual(finished.get("gate_outcome"), "awaiting_human")
