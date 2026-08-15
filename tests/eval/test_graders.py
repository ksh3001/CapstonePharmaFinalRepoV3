from __future__ import annotations

import unittest

from packages.config.paths import repo_root
from evals.graders.deterministic import (
    l0_contract,
    l1_deny_list,
    l3_trajectory,
    l4_subgroup_spread,
    l6_byte_identical,
)
from evals.run_evals import main
from packages.kernel.canonical import dumps
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import batch_pack
from packages.orchestrator.graph import DECLARED_STEPS
from tests.helpers import load_pub


class EvalHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_l0_l1_l3_l4_l6_pass_on_pub01(self) -> None:
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        self.assertTrue(l0_contract(pack, "batch_response.schema.json")["passed"])
        self.assertTrue(l1_deny_list(pack)["passed"])
        self.assertTrue(l3_trajectory(DECLARED_STEPS)["passed"])
        self.assertTrue(l4_subgroup_spread(0.0)["passed"])
        self.assertFalse(l4_subgroup_spread(0.2)["passed"])
        blob = dumps(pack)
        self.assertTrue(l6_byte_identical(blob, blob, blob)["passed"])

    def test_thresholds_keep_judge_off_and_cap_subgroup_spread(self) -> None:
        text = (repo_root() / "evals" / "thresholds.yaml").read_text(encoding="utf-8")
        self.assertIn("subgroup_spread_max: 0.15", text)
        self.assertIn("judge_gating: false", text)

    def test_run_evals_main_is_green(self) -> None:
        self.assertEqual(main(), 0)
