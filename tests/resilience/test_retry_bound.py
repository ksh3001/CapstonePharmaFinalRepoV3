from __future__ import annotations

import unittest

from packages.config.budgets import MAX_RETRIES, default_budgets
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.orchestrator.deterministic import StdlibOrchestrator, StepFailure
from tests.helpers import load_pub


class RetryBoundTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_repeated_failure_terminates_within_retry_bound(self) -> None:
        attempts = {"count": 0}

        def boom(step: str) -> None:
            del step
            attempts["count"] += 1
            raise StepFailure("injected")

        budgets = default_budgets()
        pack = StdlibOrchestrator(fail_hook=boom).run({"fixture": load_pub("PUB-13"), "budgets": budgets})
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertTrue(any(item.get("reason_code") == "retry_exhausted" for item in pack["abstentions"]))
        self.assertEqual(attempts["count"], MAX_RETRIES + 1)
        self.assertLessEqual(attempts["count"], MAX_RETRIES + 1)
