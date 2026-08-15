from __future__ import annotations

import unittest

from packages.kernel.audit import audit_events, reset_audit
from packages.kernel.canonical import dumps
from packages.kernel.checkpoint import reset_replay
from packages.orchestrator.deterministic import StdlibOrchestrator
from packages.orchestrator.graph import DECLARED_STEPS
from tests.helpers import load_pub


class ExcessiveAgencyTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_audit()

    def test_undeclared_step_is_refused_and_pack_matches_clean_run(self) -> None:
        fixture = load_pub("PUB-13")
        runner = StdlibOrchestrator()
        clean = runner.run({"fixture": fixture})
        reset_replay()
        reset_audit()
        dirty = runner.run({"fixture": fixture, "proposed_steps": ["exfiltrate", "allocate"]})
        self.assertEqual(dumps(clean), dumps(dirty))
        self.assertEqual(dirty["human_review"]["orchestration"]["steps"], list(DECLARED_STEPS))
        self.assertTrue(any(item.get("event") == "excessive_agency" for item in audit_events()))
        self.assertNotIn("exfiltrate", dirty["human_review"]["orchestration"]["steps_completed"])
