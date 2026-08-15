from __future__ import annotations

import unittest

from packages.config.budgets import MAX_TOKENS_PER_REQUEST, default_budgets
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.orchestrator.deterministic import StdlibOrchestrator
from tests.helpers import load_pub


class BudgetStopTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_step_budget_emits_valid_partial_pack(self) -> None:
        budgets = default_budgets()
        budgets["max_steps"] = 2
        pack = StdlibOrchestrator().run({"fixture": load_pub("PUB-13"), "budgets": budgets})
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertEqual(pack["gate_outcome"], "partial_coverage")
        self.assertEqual(pack["execution_status"], "not_executed")
        self.assertTrue(pack["no_side_effects"])
        self.assertTrue(any(item.get("reason_code") == "budget_stop" for item in pack["abstentions"]))
        self.assertLess(len(pack["human_review"]["orchestration"]["steps_completed"]), 9)

    def test_token_ceiling_stops_without_shortening_an_answer(self) -> None:
        self.assertEqual(MAX_TOKENS_PER_REQUEST, 50000)
        budgets = default_budgets()
        pack = StdlibOrchestrator().run(
            {
                "fixture": load_pub("PUB-13"),
                "budgets": budgets,
                "token_usage": MAX_TOKENS_PER_REQUEST + 1,
            }
        )
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertTrue(any(item.get("reason_code") == "budget_stop" for item in pack["abstentions"]))
        self.assertEqual(pack["gate_outcome"], "partial_coverage")
        self.assertTrue(any(item.get("exhausted") == "tokens" for item in pack["abstentions"]))

    def test_undeclared_budget_refuses_to_start(self) -> None:
        pack = StdlibOrchestrator().run({"fixture": load_pub("PUB-13"), "budgets": {}})
        validate(pack, resolve_contract("advisory_nonexecuting"))
        self.assertTrue(any(item.get("reason_code") == "undeclared_budget" for item in pack["abstentions"]))
        self.assertEqual(pack["gate_outcome"], "abstained")
