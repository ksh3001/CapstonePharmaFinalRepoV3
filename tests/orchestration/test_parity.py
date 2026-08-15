from __future__ import annotations

import os
import unittest

from packages.kernel.checkpoint import reset_replay
from packages.orchestrator.deterministic import StdlibOrchestrator
from packages.orchestrator.graph import DECLARED_STEPS
from services.integration.langgraph.adapter import LangGraphOrchestrator
from tests.helpers import load_pub
from packages.kernel.canonical import dumps


def _request(name: str) -> dict:
    fixture = load_pub(name)
    return {"fixture": fixture, "workflow": str((fixture.get("scenario") or {}).get("workflow") or "")}


def _strip_runner(pack: dict) -> bytes:
    clone = dict(pack)
    review = dict(clone.get("human_review") or {})
    orch = dict(review.get("orchestration") or {})
    orch.pop("runner", None)
    review["orchestration"] = orch
    clone["human_review"] = review
    return dumps(clone)


class OrchestratorParityTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_langgraph_adapter_declares_the_same_steps(self) -> None:
        self.assertEqual(LangGraphOrchestrator().declared_steps(), DECLARED_STEPS)

    def test_all_fifteen_fixtures_are_byte_identical_across_runners(self) -> None:
        stdlib = StdlibOrchestrator()
        langgraph = LangGraphOrchestrator()
        for index in range(1, 16):
            name = f"PUB-{index:02d}"
            with self.subTest(fixture=name):
                reset_replay()
                left = stdlib.run(_request(name))
                reset_replay()
                right = langgraph.run(_request(name))
                self.assertEqual(_strip_runner(left), _strip_runner(right))

    def test_model_substitution_does_not_change_pack_bytes(self) -> None:
        fixture = load_pub("PUB-13")
        old = os.environ.get("AEGIS_MODEL")
        try:
            os.environ["AEGIS_MODEL"] = "large-1"
            reset_replay()
            first = StdlibOrchestrator().run({"fixture": fixture})
            os.environ["AEGIS_MODEL"] = "small-7b"
            reset_replay()
            second = LangGraphOrchestrator().run({"fixture": fixture})
            self.assertEqual(_strip_runner(first), _strip_runner(second))
        finally:
            if old is None:
                os.environ.pop("AEGIS_MODEL", None)
            else:
                os.environ["AEGIS_MODEL"] = old
