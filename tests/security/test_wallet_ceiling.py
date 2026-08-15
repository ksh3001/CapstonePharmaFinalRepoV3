from __future__ import annotations

import unittest

from packages.finops.wallet import admit, record_spend, remaining, reset_wallet, WALLET_CEILING
from packages.kernel.checkpoint import reset_replay
from packages.orchestrator.deterministic import StdlibOrchestrator
from tests.helpers import load_pub


class WalletCeilingTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        reset_wallet()

    def tearDown(self) -> None:
        reset_wallet()

    def test_exhausted_wallet_refuses_new_run(self) -> None:
        record_spend(WALLET_CEILING)
        self.assertFalse(admit())
        self.assertEqual(remaining(), 0)
        pack = StdlibOrchestrator().run({"fixture": load_pub("PUB-13")})
        self.assertTrue(any(item.get("reason_code") == "budget_stop" for item in pack["abstentions"]))
        self.assertEqual(pack["gate_outcome"], "abstained")
