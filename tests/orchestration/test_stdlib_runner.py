from __future__ import annotations

import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.orchestrator.deterministic import StdlibOrchestrator
from packages.orchestrator.graph import DECLARED_STEPS
from packages.orchestrator.resolve import resolve_orchestrator
from tests.helpers import load_pub


class StdlibRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_declared_graph_is_fixed(self) -> None:
        self.assertEqual(
            DECLARED_STEPS,
            (
                "admit",
                "plan",
                "retrieve",
                "project_graph",
                "reconcile",
                "annotate",
                "approve",
                "package",
                "validate_emit",
            ),
        )

    def test_pub13_through_stdlib_runner_validates(self) -> None:
        pack = resolve_orchestrator().run({"fixture": load_pub("PUB-13")})
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertEqual(pack["human_review"]["orchestration"]["runner"], "stdlib")
        self.assertEqual(pack["human_review"]["orchestration"]["steps_completed"], list(DECLARED_STEPS))
        self.assertEqual(pack["execution_status"], "not_executed")

    def test_assessment_resolver_is_stdlib(self) -> None:
        self.assertIsInstance(resolve_orchestrator(), StdlibOrchestrator)
